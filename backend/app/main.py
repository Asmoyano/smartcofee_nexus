from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import productos, mesas, pedidos

# Crear de forma automática las tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SmartCoffee Nexus API",
    description="Backend para el sistema de atención y gestión de pedidos vía QR - Sprint 1",
    version="1.0.0"
)

# ==========================================
# CONFIGURACIÓN DE CORS (Para conectar con Vite)
# ==========================================
# Permite el frontend local (que correrá en el puerto 5173 de Vite) 
# pueda consumir los endpoints del backend sin bloqueos de seguridad del navegador.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://192.168.18.54:5173", "http://10.148.251.229:5173"],  # Ajustar según IP local
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, PUT, DELETE, PATCH, etc.
    allow_headers=["*"],
)

# ==========================================
# INCLUSIÓN DE ROUTERS MODULARES
# ==========================================
app.include_router(productos.router)
app.include_router(mesas.router)
app.include_router(pedidos.router)

@app.get("/", tags=["Root"])
def root():
    """Endpoint de control para verificar que el servidor responda correctamente."""
    return {
        "status": "online",
        "proyecto": "SmartCoffee Nexus",
        "sprint": 1,
        "documentacion": "/docs"
    }