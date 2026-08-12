from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


# ─── CATEGORÍA ───────────────────────────────────────────────────────────────
class CategoriaBase(BaseModel):
    nombre: str = Field(..., max_length=100, examples=["Cafés", "Postres"])

class CategoriaResponse(CategoriaBase):
    id_categoria: int
    class Config:
        from_attributes = True


# ─── INSUMO ───────────────────────────────────────────────────────────────────
class InsumoBase(BaseModel):
    nombre: str = Field(..., min_length=1)
    stock_actual: float = Field(..., ge=0.0)
    stock_minimo: float = Field(..., ge=0.0)
    unidad_medida: str = Field(..., min_length=1)
    es_alergeno: bool = False

class InsumoCreate(InsumoBase):
    pass

class InsumoUpdate(BaseModel):
    nombre: Optional[str] = None
    stock_actual: Optional[float] = Field(None, ge=0.0)
    stock_minimo: Optional[float] = Field(None, ge=0.0)
    unidad_medida: Optional[str] = None
    es_alergeno: Optional[bool] = None

class InsumoResponse(InsumoBase):
    id_insumo: int
    class Config:
        from_attributes = True


# ─── INSUMO EN RECETA ─────────────────────────────────────────────────────────
class InsumoEnReceta(BaseModel):
    id_insumo: int
    nombre: str
    cantidad_usada: float
    unidad_medida: str
    es_alergeno: bool
    class Config:
        from_attributes = True


# ─── PRODUCTO ─────────────────────────────────────────────────────────────────
class ProductoBase(BaseModel):
    id_categoria: int
    nombre: str = Field(..., max_length=150)
    descripcion: Optional[str] = None
    precio: float = Field(..., gt=0)
    imagen_url: Optional[str] = Field(None, max_length=300)
    disponible: bool = True

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    id_categoria: Optional[int] = None
    nombre: Optional[str] = Field(None, max_length=150)
    descripcion: Optional[str] = None
    precio: Optional[float] = Field(None, gt=0)
    imagen_url: Optional[str] = Field(None, max_length=300)
    disponible: Optional[bool] = None

class ProductoResponse(ProductoBase):
    id_producto: int
    es_alergeno: bool = False
    class Config:
        from_attributes = True

class ProductoDetalleResponse(ProductoBase):
    id_producto: int
    es_alergeno: bool = False
    insumos: List[InsumoEnReceta] = []
    class Config:
        from_attributes = True


# ─── DETALLE DE PEDIDO ────────────────────────────────────────────────────────
class DetallePedidoCreate(BaseModel):
    id_producto: int
    cantidad_pedida: int = Field(..., gt=0)

class DetallePedidoResponse(BaseModel):
    id_producto: int
    cantidad_pedida: int
    sub_total: float
    producto: ProductoResponse
    class Config:
        from_attributes = True


# ─── PEDIDO ───────────────────────────────────────────────────────────────────
class PedidoCreate(BaseModel):
    id_mesa: int
    id_cliente: Optional[int] = None
    id_usuario: Optional[int] = None
    detalles: List[DetallePedidoCreate] = Field(..., min_length=1)

class PedidoEstadoUpdate(BaseModel):
    estado: str = Field(..., description="Estados válidos: pendiente, en_preparacion, listo, entregado, cancelado")

class PedidoResponse(BaseModel):
    id_pedido: int
    id_mesa: int
    id_cliente: Optional[int]
    id_usuario: Optional[int]
    estado: str
    fecha_creacion: datetime
    fecha_entrega: Optional[datetime]
    fecha_inicio_prep: Optional[datetime] = None
    fecha_fin_prep: Optional[datetime] = None
    total_pago: float
    detalles: List[DetallePedidoResponse]
    class Config:
        from_attributes = True


# ─── RECETA ───────────────────────────────────────────────────────────────────
class RecetaBase(BaseModel):
    id_insumo: int
    cantidad_usada: float = Field(..., gt=0.0)

class RecetaCreate(RecetaBase):
    pass

class RecetaResponse(RecetaBase):
    id_insumo: int
    id_producto: int
    class Config:
        from_attributes = True


# ─── MESA ─────────────────────────────────────────────────────────────────────
class MesaResponse(BaseModel):
    id_mesa: int
    qr_code: str = Field(..., max_length=100)
    class Config:
        from_attributes = True


# ─── CLIENTE ──────────────────────────────────────────────────────────────────
class ClienteBase(BaseModel):
    nombre: str = Field(..., max_length=150)
    correo: Optional[EmailStr] = None
    documento_identidad: Optional[str] = Field(None, max_length=20)

class ClienteResponse(ClienteBase):
    id_cliente: int
    class Config:
        from_attributes = True