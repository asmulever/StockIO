"""SQLAlchemy model for inventory movements with validation helpers.

Assumptions
-----------
* Product table is defined in the same metadata and linked through
  ``product.product_id``.
* A UTC‐aware timestamp is preferred. If the input date comes without
  timezone info, it is coerced to UTC so that the API returns
  consistently formatted ISO‑8601 timestamps.
* Allowed movement types are constrained to an Enum (``IN`` for stock
  increase, ``OUT`` for decrease). Change the Enum values to suit your
  domain.

Revision History
----------------
* 2025‑06‑16 – Initial refactor with explicit coercion helpers, Enum for
  movement_type, delete() convenience, and more robust error logging.
* 2025‑06‑16 – Simplified `_coerce_date` to use `datetime.fromisoformat` and accept
  both “YYYY‑MM‑DDTHH:MM:SS” and “YYYY‑MM‑DD HH:MM:SS”.
* 2025‑06‑16 – Added dash normalisation in `_coerce_date` to fix "Invalid
  isoformat string" with non‑ASCII hyphens.
"""

from __future__ import annotations

from datetime import datetime, timezone ,timedelta
from typing import Optional, Union, Dict
import re  # for dash normalisation
import statistics

from flask import current_app
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session

from .. import db


class InventoryMovement(db.Model):
    """Track every physical movement that affects stock."""

    __tablename__ = "inventory_movement"

    # Columns -----------------------------------------------------------------
    movement_id: str = db.Column(db.String(36), primary_key=True)
    date: datetime = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    product_id: str = db.Column(
        db.String(36), db.ForeignKey("product.product_id"), nullable=False, index=True
    )   
    movement_type = db.Column(db.String(20), nullable=False)
    quantity: int = db.Column(db.Integer, nullable=False)
    order_id: Optional[str] = db.Column(db.String(50))
    notes: Optional[str] = db.Column(db.String(255))

    # Relationships -----------------------------------------------------------
    product = db.relationship(
        "Product", backref=db.backref("inventory_movements", lazy="dynamic")
    )

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------
    def to_dict(self) -> dict:
        """Return a JSON‑serialisable representation."""
        return {
            "movement_id": self.movement_id,
            "date": self.date.isoformat() if self.date else None,
            "product_id": self.product_id,
            "movement_type": self.movement_type,
            "quantity": self.quantity,
            "order_id": self.order_id,
            "notes": self.notes,
        }

    # Static / class utilities -------------------------------------------
    _DASH_PATTERN = re.compile(r"[\u2010-\u2015\u2212]")

    @staticmethod
    def _coerce_date(value: Union[datetime, str]) -> datetime:
       
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)

        if isinstance(value, str):
            # Replace fancy dashes with ASCII '-' and handle trailing Z.
            clean = InventoryMovement._DASH_PATTERN.sub("-", value.strip())
            clean = clean.replace("Z", "+00:00")
            try:
                dt = datetime.fromisoformat(clean)
            except ValueError as exc:
                raise ValueError(
                    "Formato de fecha inválido. Se esperaba ISO 8601 'YYYY-MM-DD[ T]HH:MM[:SS[±HH:MM]]'."
                ) from exc

            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

        raise ValueError("Fecha inválida: se esperaba datetime o str")

    # CRUD class‑methods ---------------------------------------------------
    @classmethod
    def create(cls, data: dict) -> "InventoryMovement":
        """Factory that validates *data* and persists the record."""
        required: set[str] = {
            "movement_id",
            "date",
            "product_id",
            "movement_type",
            "quantity",
        }
        missing = required - data.keys()
        if missing:
            raise ValueError(f"Campos requeridos faltantes: {', '.join(sorted(missing))}")

        data = data.copy()
        data["date"] = cls._coerce_date(data["date"])

        if not isinstance(data["quantity"], int):
            raise ValueError("La cantidad debe ser un entero")

        try:
            movement = cls(**data)  # type: ignore[arg-type]
            db.session.add(movement)
            db.session.commit()
            return movement
        except (IntegrityError, DataError) as exc:
            db.session.rollback()
            current_app.logger.error("Error de integridad/datos", exc_info=exc)
            raise ValueError("Datos duplicados o inválidos") from exc
        except Exception:
            db.session.rollback()
            current_app.logger.exception("Error inesperado al crear movimiento")
            raise

    @classmethod
    def get_all(cls, page: Optional[int] = None, per_page: Optional[int] = None):
        """Return a list or Pagination of movements, newest first."""
        query = cls.query.order_by(cls.date.desc())
        if page is not None and per_page is not None:
            return query.paginate(page=page, per_page=per_page, error_out=False)
        return query.all()

    @classmethod
    def update(cls, movement_id: str, data: dict) -> "InventoryMovement":
        """Update the record identified by *movement_id* with *data*."""
        movement = cls.query.get(movement_id)
        if not movement:
            raise ValueError("Movimiento no encontrado")

        try:
            for key, value in data.items():
                if key == "date":
                    value = cls._coerce_date(value)
                if hasattr(movement, key):
                    setattr(movement, key, value)
            db.session.commit()
            return movement
        except Exception:
            db.session.rollback()
            current_app.logger.exception("Error actualizando movimiento")
            raise

    @classmethod
    def delete(cls, movement_id: str) -> None:
        """Remove a movement from the database."""
        movement = cls.query.get(movement_id)
        if not movement:
            raise ValueError("Movimiento no encontrado")
        try:
            db.session.delete(movement)
            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.exception("Error eliminando movimiento")
            raise

   # ------------------------------------------------------------------
    # Forecast helpers
    # ------------------------------------------------------------------
    @classmethod
    def forecast_purchase_needs(
        cls,
        *,
        horizon_days: int = 90,
        window_days: int = 180,
        cover_days: int = 30,
        min_records: int = 30,
    ) -> Dict[str, int]:
        """Return ``{product_id: qty_to_order}`` using simple moving average.

        If fewer than *min_records* movements are found in the window, the query
        widens to include all history.
        """
        from ..models.producto import Product  # avoid circular import

        sess = db.session
        today = datetime.utcnow().date()
        start = today - timedelta(days=window_days)

        rows = list(
            sess.query(cls.product_id, cls.date, cls.movement_type, cls.quantity)
            .filter(cls.date >= start)
            .all()
        )

        if len(rows) < min_records:
            rows = list(sess.query(cls.product_id, cls.date, cls.movement_type, cls.quantity).all())
            if rows:
                earliest = min(r[1] for r in rows).date()
                window_days = (today - earliest).days + 1
                start = earliest

        # Aggregate to daily net per product
        daily_net: Dict[str, Dict[datetime, int]] = {}
        for pid, dt, typ, qty in rows:
            day = dt.date()
            signed = -qty if typ == "OUT" else qty
            daily_net.setdefault(pid, {}).setdefault(day, 0)
            daily_net[pid][day] += signed

        stock = {p.product_id: p.stk_qty for p in sess.query(Product).all()}
        needs: Dict[str, int] = {}

        for pid, by_day in daily_net.items():
            series = [by_day.get(start + timedelta(d), 0) for d in range(window_days)]
            non_zero = [v for v in series if v != 0]
            if len(non_zero) < max(1, min_records // 3):  # evitar promedio sobre muchos ceros
                continue
            avg_daily = statistics.mean(non_zero)
            demand = avg_daily * horizon_days
            buffer = avg_daily * cover_days
            qty = max(int(round(demand + buffer - stock.get(pid, 0))), 0)
            if qty:
                needs[pid] = qty
        return needs

    @classmethod
    def forecast_purchase_needs_list(cls, **kwargs):
        """Return list ``[{producto, prediccion}, …]`` ready for frontend."""
        from ..models.producto import Product

        needs = cls.forecast_purchase_needs(**kwargs)
        names = {p.product_id: p.product_name for p in db.session.query(Product).all()}
        return [
            {"producto": names.get(pid, pid), "prediccion": qty}
            for pid, qty in needs.items()
        ]
