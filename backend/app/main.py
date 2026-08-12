import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.database import Base, engine
from app.routers import productos, mesas, pedidos, inventario

load_dotenv()

# Crea las tablas automáticamente si no existen.
# En producción con PostgreSQL esto crea el schema en el primer arranque.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SmartCoffee Nexus API",
    description="Sistema de autoservicio digital para cafeterías basado en QR.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS: en producción permite el dominio de Vercel configurado en .env.
# En desarrollo permite localhost y cualquier IP local.
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173"
).split(",")

# Siempre incluimos el comodín para Vercel preview deployments
ALLOWED_ORIGINS += ["https://*.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(productos.router)
app.include_router(mesas.router)
app.include_router(pedidos.router)
app.include_router(inventario.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "status": "online",
        "proyecto": "SmartCoffee Nexus",
        "version": "2.0.0",
        "docs": "/docs"
    }
