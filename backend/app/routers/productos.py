from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Producto, Categoria, Receta, Insumo
from app.schemas import (
    ProductoCreate, ProductoUpdate,
    ProductoResponse, ProductoDetalleResponse,
    CategoriaResponse, InsumoEnReceta
)

router = APIRouter(prefix="/productos", tags=["Productos & Catálogo"])


# ─── GET /productos ───────────────────────────────────────────────────────────
@router.get("", response_model=List[ProductoResponse])
def listar_productos(categoria_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Producto).filter(Producto.disponible == True)
    if categoria_id:
        query = query.filter(Producto.id_categoria == categoria_id)
    productos = query.all()

    # CORRECCIÓN Bug #003: ahora sí calcula es_alergeno por producto
    resultado = []
    for p in productos:
        tiene_alergeno = any(
            receta.insumo.es_alergeno for receta in p.recetas
        )
        p_response = ProductoResponse(
            id_producto=p.id_producto,
            id_categoria=p.id_categoria,
            nombre=p.nombre,
            descripcion=p.descripcion,
            precio=p.precio,
            imagen_url=p.imagen_url,
            disponible=p.disponible,
            es_alergeno=tiene_alergeno
        )
        resultado.append(p_response)
    return resultado


# ─── GET /productos/categorias ────────────────────────────────────────────────
@router.get("/categorias", response_model=List[CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    """Retorna todas las categorías para armar las pestañas del frontend."""
    return db.query(Categoria).all()


# ─── GET /productos/{id} ──────────────────────────────────────────────────────
@router.get("/{id_producto}", response_model=ProductoDetalleResponse)
def obtener_producto(id_producto: int, db: Session = Depends(get_db)):
    """
    HU01: Detalle completo de un producto.
    HU02 / TA02-2: Incluye la lista de insumos con sus cantidades y flag de alérgeno.
    """
    producto = db.query(Producto).filter(
        Producto.id_producto == id_producto,
        Producto.disponible == True
    ).first()

    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {id_producto} no encontrado o no disponible."
        )

    # Construir lista de insumos desde la relación Receta → Insumo (TA02-2)
    insumos_detalle = []
    tiene_alergeno = False
    for receta in producto.recetas:
        insumo = receta.insumo
        if insumo.es_alergeno:
            tiene_alergeno = True
        insumos_detalle.append(InsumoEnReceta(
            id_insumo=insumo.id_insumo,
            nombre=insumo.nombre,
            cantidad_usada=receta.cantidad_usada,
            unidad_medida=insumo.unidad_medida,
            es_alergeno=insumo.es_alergeno
        ))

    return ProductoDetalleResponse(
        id_producto=producto.id_producto,
        id_categoria=producto.id_categoria,
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        precio=producto.precio,
        imagen_url=producto.imagen_url,
        disponible=producto.disponible,
        es_alergeno=tiene_alergeno,
        insumos=insumos_detalle
    )


# ─── POST /productos ──────────────────────────────────────────────────────────
@router.post("", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def crear_producto(payload: ProductoCreate, db: Session = Depends(get_db)):
    """
    TA01-2: Registra un nuevo producto en la carta del establecimiento.
    Valida que la categoría exista antes de insertarlo.
    """
    categoria = db.query(Categoria).filter(
        Categoria.id_categoria == payload.id_categoria
    ).first()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La categoría con ID {payload.id_categoria} no existe."
        )

    nuevo_producto = Producto(**payload.model_dump())
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    return nuevo_producto


# ─── PUT /productos/{id} ──────────────────────────────────────────────────────
@router.put("/{id_producto}", response_model=ProductoResponse)
def actualizar_producto(
    id_producto: int,
    payload: ProductoUpdate,
    db: Session = Depends(get_db)
):
    """
    TA01-2: Actualiza los datos de un producto existente.
    Solo modifica los campos que se envían en el body (actualización parcial).
    Permite marcar un producto como no disponible, lo que activa el Bug #004
    cuando ese producto se intenta pedir desde el cliente.
    """
    producto = db.query(Producto).filter(
        Producto.id_producto == id_producto
    ).first()
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {id_producto} no encontrado."
        )

    # Aplicar solo los campos enviados (ignorar los None)
    datos_actualizar = payload.model_dump(exclude_unset=True)
    for campo, valor in datos_actualizar.items():
        setattr(producto, campo, valor)

    db.commit()
    db.refresh(producto)
    return producto