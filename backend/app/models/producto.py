from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from flask import current_app
from .. import db

class Product(db.Model):
    __tablename__ = "product"

    product_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    product_name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), nullable=False, unique=True)
    unit_of_measure = db.Column(db.String(20), nullable=False)
    cost = db.Column(db.Numeric(10, 2), nullable=False)
    sale_price = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    stk_qty = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime,
                         default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Versión única del método to_dict"""
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'sku': self.sku,
            'unit_of_measure': self.unit_of_measure,
            'cost': float(self.cost),
            'sale_price': float(self.sale_price),
            'category': self.category,
            'location': self.location,
            'stk_qty': self.stk_qty,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def create(cls, data: dict):
        try:
            required_fields = ['product_name', 'sku', 'unit_of_measure', 'cost', 'sale_price']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Campo requerido faltante: {field}")

            product = cls(**data)
            db.session.add(product)
            db.session.commit()
            return product

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"Error de integridad: {str(e)}")
            raise ValueError("SKU ya existe o datos inválidos") from e
        except DataError as e:
            db.session.rollback()
            current_app.logger.error(f"Error en datos: {str(e)}")
            raise ValueError("Datos proporcionados inválidos") from e
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error inesperado: {str(e)}", exc_info=True)
            raise

    @classmethod
    def get_all(cls, active_only=True):
        query = cls.query
        if active_only:
            query = query.filter_by(active=True)
        return query.all()

    @classmethod
    def get_by_id(cls, product_id):
        return cls.query.filter_by(product_id=product_id).first()

         # ─── Actualiza campos arbitrarios en la instancia ─────────────
    def update(self, data: dict):
        try:
            for k, v in data.items():
                # Solo permite campos existentes (evita AttributeError)
                if hasattr(self, k):
                    setattr(self, k, v)
            db.session.commit()
            return self
        except (IntegrityError, DataError) as e:
            db.session.rollback()
            current_app.logger.error(f"Error al actualizar producto: {str(e)}")
            raise ValueError("Datos de actualización inválidos") from e

    # ─── Baja lógica / reactivación ───────────────────────────────
    def deactivate(self):
        self.active = False
        db.session.commit()

    def activate(self):
        self.active = True
        db.session.commit()

    # ─── Ajuste de stock (métodos de clase) ──────────────────────
    @classmethod
    def add_stock(cls, product_id: str, qty: int):
        if qty <= 0:
            raise ValueError("La cantidad a agregar debe ser mayor que cero")
        prod = cls.get_by_id(product_id)
        if not prod:
            raise ValueError("Producto no encontrado")
        prod.stk_qty += qty
        db.session.commit()
        return prod

    @classmethod
    def subtract_stock(cls, product_id: str, qty: int):
        if qty <= 0:
            raise ValueError("La cantidad a descontar debe ser mayor que cero")
        prod = cls.get_by_id(product_id)
        if not prod:
            raise ValueError("Producto no encontrado")
        if prod.stk_qty < qty:
            raise ValueError("Stock insuficiente")
        prod.stk_qty -= qty
        db.session.commit()
        return prod

    # ─── Utilitario de búsqueda por SKU ───────────────────────────
    @classmethod
    def get_by_sku(cls, sku: str):
        return cls.query.filter_by(sku=sku).first()