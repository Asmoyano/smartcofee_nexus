from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# 1. SCHEMAS DE CATEGORÍA (HU01)
class CategoriaBase(BaseModel):
    nombre: str = Field(..., max_length=100, examples=["Cafés", "Postres"])

class CategoriaResponse(CategoriaBase):
    id_categoria: int

    class Config:
        from_attributes = True

# --- Esquemas para Insumos e Inventario ---
class InsumoBase(BaseModel):
    nombre: str = Field(..., min_length=1)
    stock_actual: float = Field(..., ge=0.0)
    stock_minimo: float = Field(..., ge=0.0)
    unidad_medida: str = Field(..., min_length=1)
    es_alergeno: bool = False

class InsumoCreate(InsumoBase):
    pass

class InsumoResponse(InsumoBase):
    id_insumo: int

    class Config:
        from_attributes = True

# ─── INSUMO EN RECETA (TA02-2) ───────────────────────────────────────────────
class InsumoEnReceta(BaseModel):
    id_insumo: int
    nombre: str
    cantidad_usada: float
    unidad_medida: str
    es_alergeno: bool
 
    class Config:
        from_attributes = True 

# 2. SCHEMAS DE PRODUCTO (HU01, HU02)
class ProductoBase(BaseModel):
    id_categoria: int
    nombre: str = Field(..., max_length=150)
    descripcion: Optional[str] = None
    precio: float = Field(..., gt=0)
    imagen_url: Optional[str] = Field(None, max_length=300)
    disponible: bool = True
 
 
# Schema nuevo (TA01-2): entrada para POST /productos
class ProductoCreate(ProductoBase):
    pass
 
 
# Schema nuevo (TA01-2): entrada para PUT /productos/{id}
# Todos los campos son opcionales — solo se actualiza lo que se manda
class ProductoUpdate(BaseModel):
    id_categoria: Optional[int] = None
    nombre: Optional[str] = Field(None, max_length=150)
    descripcion: Optional[str] = None
    precio: Optional[float] = Field(None, gt=0)
    imagen_url: Optional[str] = Field(None, max_length=300)
    disponible: Optional[bool] = None
 
 
# Schema existente: respuesta básica para GET /productos (lista)
class ProductoResponse(ProductoBase):
    id_producto: int
    # BUG #003: el campo existe en el schema pero el router
    # no lo calcula — siempre devuelve False por defecto.
    es_alergeno: bool = False
 
    class Config:
        from_attributes = True
 
 
# Schema nuevo (TA02-2): respuesta extendida para GET /productos/{id}
# Incluye la lista completa de insumos/ingredientes con sus alérgenos
class ProductoDetalleResponse(ProductoBase):
    id_producto: int
    es_alergeno: bool = False
    insumos: List[InsumoEnReceta] = []
 
    class Config:
        from_attributes = True


# 3. SCHEMAS DE DETALLE DE PEDIDO (HU05)
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


# 4. SCHEMAS DE PEDIDO (HU05)
class PedidoCreate(BaseModel):
    id_mesa: int
    id_cliente: Optional[int] = None
    id_usuario: Optional[int] = None
    detalles: List[DetallePedidoCreate] = Field(..., min_length=1)

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

class PedidoEstadoUpdate(BaseModel):
    estado: str = Field(..., description="Estados válidos: Pendiente, En Preparación, Listo, Entregado")


# 5. SCHEMAS DE MESA (HU14)
class MesaResponse(BaseModel):
    id_mesa: int
    qr_code: str = Field(..., max_length=100)

    class Config:
        from_attributes = True


# 6. SCHEMAS DE CLIENTE (Opcional - HU03 / HU05)
class ClienteBase(BaseModel):
    nombre: str = Field(..., max_length=150)
    correo: Optional[EmailStr] = None
    documento_identidad: Optional[str] = Field(None, max_length=20)

class ClienteResponse(ClienteBase):
    id_cliente: int

    class Config:
        from_attributes = True

# --- Esquemas para Recetas ---
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