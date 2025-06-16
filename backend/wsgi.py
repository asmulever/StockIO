import logging
from app import create_app
from flask_cors import CORS

logging.basicConfig(level=logging.INFO)
app = create_app()

# Permitir CORS para el frontend React en localhost:5173
CORS(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)