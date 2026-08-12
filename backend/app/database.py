import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# En producción (Railway) usa DATABASE_URL con PostgreSQL.
# En desarrollo local usa SQLite si no hay variable de entorno configurada.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smartcoffee.db")

# Railway a veces entrega URLs que empiezan con "postgres://" (formato antiguo).
# SQLAlchemy requiere "postgresql://" — este fix lo corrige automáticamente.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite necesita check_same_thread=False para funcionar con FastAPI.
# PostgreSQL no necesita ese argumento, así que lo aplicamos condicionalmente.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
