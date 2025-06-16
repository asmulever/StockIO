from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token
from .models.producto import Product
from .models.movimiento import InventoryMovement
import logging

bp = Blueprint("api", __name__, url_prefix="/api")

# ─── Logging ──────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════
#  Auth
# ══════════════════════════════════════════════════════════════════════════
@bp.route("/login", methods=["POST"])
def login():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    try:
        data = request.get_json()
        if not data:
            raise ValueError("Datos JSON requeridos")

        if data.get("username") == "admin" and data.get("password") == "dog":
            access_token = create_access_token(identity="admin")
            return jsonify(access_token), 200

        return jsonify({"error": "Credenciales inválidas"}), 401

    except Exception as e:
        logger.error(f"Error en login: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 400
    
# ══════════════════════════════════════════════════════════════════════════
#  Prediccion
# ══════════════════════════════════════════════════════════════════════════
@bp.route("/get_prediction", methods=["GET"])
@jwt_required()
def get_prediction():    
    try:
        needs  = InventoryMovement.forecast_purchase_needs_list()
        return jsonify(needs), 200
    except Exception as e:
        logger.error(f"Error obteniendo productos: {str(e)}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500
    
# ══════════════════════════════════════════════════════════════════════════
#  Stock
# ══════════════════════════════════════════════════════════════════════════
@bp.route("/get_stocks", methods=["GET"])
@jwt_required()
def get_stocks():
    """Lista todos los movimientos activos (o todos, con ?all=true)."""
    try:        
        stkmovs = InventoryMovement.get_all()
        return jsonify([m.to_dict() for m in stkmovs]), 200
    except Exception as e:
        logger.error(f"Error obteniendo stock: {str(e)}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500
# ══════════════════════════════════════════════════════════════════════════
#  Productos
# ══════════════════════════════════════════════════════════════════════════
@bp.route("/get_products", methods=["GET"])
@jwt_required()
def get_products():
    """Lista todos los productos activos (o todos, con ?all=true)."""
    try:
        active_only = request.args.get("all") != "true"
        productos = Product.get_all(active_only=active_only)
        return jsonify([p.to_dict() for p in productos]), 200
    except Exception as e:
        logger.error(f"Error obteniendo productos: {str(e)}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500

    
@bp.route("/products", methods=["POST", "OPTIONS"])
@jwt_required()
def create_product():
    """Crea un producto nuevo."""
    try:
        data = request.get_json()
        prod = Product.create(data)
        return jsonify(prod.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error creando producto: {str(e)}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500


@bp.route("/products/<product_id>", methods=["PUT", "PATCH", "OPTIONS"])
@jwt_required()
def update_product(product_id):
    """Actualiza campos arbitrarios de un producto."""
    try:
        producto = Product.get_by_id(product_id)
        if not producto:
            return jsonify({"error": "Producto no encontrado"}), 404

        data = request.get_json()
        producto.update(data)                       # ← usa método de instancia
        return jsonify(producto.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error actualizando producto: {str(e)}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500


@bp.route("/products/<product_id>/activate", methods=["PATCH", "OPTIONS"])
@jwt_required()
def activate_product(product_id):
    """Reactiva un producto dado de baja lógicamente."""
    producto = Product.get_by_id(product_id)
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404
    producto.activate()
    return jsonify({"msg": "Producto activado"}), 200


@bp.route("/products/<product_id>/deactivate", methods=["PATCH", "OPTIONS"])
@jwt_required()
def deactivate_product(product_id):
    """Baja lógica del producto."""
    producto = Product.get_by_id(product_id)
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404
    producto.deactivate()
    return jsonify({"msg": "Producto desactivado"}), 200


# ══════════════════════════════════════════════════════════════════════════
#  Stock
# ══════════════════════════════════════════════════════════════════════════
@bp.route("/products/<product_id>/stock/add", methods=["PATCH", "OPTIONS"])
@jwt_required()
def add_stock(product_id):
    """Incrementa el stock de un producto."""
    try:
        qty = request.get_json().get("qty", 0)
        producto = Product.add_stock(product_id, qty)
        return jsonify(producto.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Añadiendo stock: {str(e)}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500


@bp.route("/products/<product_id>/stock/subtract", methods=["PATCH", "OPTIONS"])
@jwt_required()
def subtract_stock(product_id):
    """Descuenta stock (p.ej., venta o salida)."""
    try:
        qty = request.get_json().get("qty", 0)
        producto = Product.subtract_stock(product_id, qty)
        return jsonify(producto.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Descontando stock: {str(e)}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500
