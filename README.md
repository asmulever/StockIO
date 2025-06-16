mi-gestor-stock/
│
├── backend/                  # API en Flask
│   ├── app/
│   │   ├── __init__.py       # Inicialización del backend
│   │   ├── models.py         # SQLAlchemy ORM (Product, Inventory, etc.)
│   │   ├── routes.py         # Endpoints REST
│   │   ├── services.py       # Lógica (predicción, stock)
│   │   ├── auth.py           # Login / JWT
│   ├── requirements.txt
│   ├── wsgi.py
│
├──frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.jsx          # Controla toda la UI: login + dashboard + productos
│   │   ├── index.js         # Entrypoint
│   │   └── api.js           # Funciones fetch() a la API
│   ├── package.json
│
├── docker-compose.yml       # Orquestación backend + frontend
├── Dockerfile.backend        # Imagen Flask
├── Dockerfile.frontend       # Imagen React
└── README.md
