from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre       = Column(String(100), nullable=False, unique=True)

    productos = relationship("Producto", back_populates="categoria")


class Insumo(Base):
    __tablename__ = "insumos"

    id_insumo     = Column(Integer, primary_key=True, index=True)
    nombre        = Column(String(100), nullable=False)
    stock_actual  = Column(Float, nullable=False, default=0.0)
    stock_minimo  = Column(Float, nullable=False, default=0.0)
    unidad_medida = Column(String(20), nullable=False)
    es_alergeno   = Column(Boolean, nullable=False, default=False)

    recetas = relationship("Receta", back_populates="insumo")



class Producto(Base):
    __tablename__ = "productos"

    id_producto  = Column(Integer, primary_key=True, index=True)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"), nullable=False)
    nombre       = Column(String(150), nullable=False)
    descripcion  = Column(Text, nullable=True)
    precio       = Column(Float, nullable=False)
    imagen_url   = Column(String(300), nullable=True)
    disponible   = Column(Boolean, nullable=False, default=True)

    categoria       = relationship("Categoria", back_populates="productos")
    recetas         = relationship("Receta", back_populates="producto")
    detalles_pedido = relationship("DetallePedido", back_populates="producto")

class Receta(Base):
    __tablename__ = "recetas"

    id_producto    = Column(Integer, ForeignKey("productos.id_producto"), primary_key=True)
    id_insumo      = Column(Integer, ForeignKey("insumos.id_insumo"), primary_key=True)
    cantidad_usada = Column(Float, nullable=False)

    producto = relationship("Producto", back_populates="recetas")
    insumo   = relationship("Insumo", back_populates="recetas")


class Mesa(Base):
    __tablename__ = "mesas"

    id_mesa  = Column(Integer, primary_key=True, index=True)
    qr_code  = Column(String(100), nullable=False, unique=True)

    pedidos = relationship("Pedido", back_populates="mesa")


class Cliente(Base):
    __tablename__ = "clientes"

    id_cliente         = Column(Integer, primary_key=True, index=True)
    nombre             = Column(String(150), nullable=False)
    correo             = Column(String(200), nullable=True, unique=True)
    documento_identidad = Column(String(20), nullable=True)

    pedidos = relationship("Pedido", back_populates="cliente")


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario    = Column(Integer, primary_key=True, index=True)
    nombre        = Column(String(150), nullable=False)
    rol           = Column(String(50), nullable=False)  # admin, cocinero, mesero
    password_hash = Column(String(255), nullable=False)

    pedidos = relationship("Pedido", back_populates="usuario")


class Pedido(Base):
    __tablename__ = "pedidos"

    id_pedido      = Column(Integer, primary_key=True, index=True)
    id_mesa        = Column(Integer, ForeignKey("mesas.id_mesa"), nullable=False)
    id_cliente     = Column(Integer, ForeignKey("clientes.id_cliente"), nullable=True)
    id_usuario     = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    estado         = Column(String(50), nullable=False, default="pendiente")
    # estados validos: pendiente | en_preparacion | listo | entregado | cancelado
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_entrega  = Column(DateTime(timezone=True), nullable=True)
    fecha_inicio_prep = Column(DateTime, nullable=True) # Cuándo pasa a "En Preparación"
    fecha_fin_prep = Column(DateTime, nullable=True)    # Cuándo pasa a "Listo"
    total_pago     = Column(Float, nullable=False, default=0.0)

    mesa     = relationship("Mesa", back_populates="pedidos")
    cliente  = relationship("Cliente", back_populates="pedidos")
    usuario  = relationship("Usuario", back_populates="pedidos")
    detalles = relationship("DetallePedido", back_populates="pedido")
    feedback = relationship("Feedback", back_populates="pedido", uselist=False)


class DetallePedido(Base):
    __tablename__ = "detalles_pedido"

    id_pedido       = Column(Integer, ForeignKey("pedidos.id_pedido"), primary_key=True)
    id_producto     = Column(Integer, ForeignKey("productos.id_producto"), primary_key=True)
    cantidad_pedida = Column(Integer, nullable=False)
    sub_total       = Column(Float, nullable=False)

    pedido   = relationship("Pedido", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_pedido")


class Feedback(Base):
    __tablename__ = "feedback"

    id_feedback = Column(Integer, primary_key=True, index=True)
    id_pedido   = Column(Integer, ForeignKey("pedidos.id_pedido"), nullable=False, unique=True)
    puntuacion  = Column(Integer, nullable=False)  # 1-5
    comentario  = Column(Text, nullable=True)

    pedido = relationship("Pedido", back_populates="feedback")