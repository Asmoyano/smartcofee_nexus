from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import asyncio
from app.database import get_db
from app.models import Pedido, DetallePedido, Producto, Mesa
from app.schemas import PedidoCreate, PedidoResponse, PedidoEstadoUpdate
from app.websocket_manager import manager  # Gestión de WebSockets activa

router = APIRouter(prefix="/pedidos", tags=["Pedidos & Órdenes"])


# ─── GET /pedidos ─────────────────────────────────────────────────────────────
@router.get("", response_model=List[PedidoResponse])
def listar_pedidos(
    estado: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    TA05-2: Lista todos los pedidos ordenados por fecha de creación ASC (FIFO).
    """
    query = db.query(Pedido).order_by(Pedido.fecha_creacion.asc())

    if estado:
        estados_validos = ["pendiente", "en_preparacion", "listo", "entregado", "cancelado"]
        if estado not in estados_validos:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Estado '{estado}' no válido. Use: {', '.join(estados_validos)}"
            )
        query = query.filter(Pedido.estado == estado)

    return query.all()


# ─── POST /pedidos ────────────────────────────────────────────────────────────
@router.post("", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
def crear_pedido(payload: PedidoCreate, db: Session = Depends(get_db)):
    """
    HU05: Registra un nuevo pedido vinculado a una mesa.
    """
    # 1. Validar que la mesa exista
    mesa = db.query(Mesa).filter(Mesa.id_mesa == payload.id_mesa).first()
    if not mesa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La mesa con ID {payload.id_mesa} no existe."
        )

    # 2. Crear cabecera del pedido
    nuevo_pedido = Pedido(
        id_mesa=payload.id_mesa,
        id_cliente=payload.id_cliente,
        id_usuario=payload.id_usuario,
        estado="pendiente",
        total_pago=0.0
    )
    db.add(nuevo_pedido)
    db.commit()
    db.refresh(nuevo_pedido)

    monto_total = 0.0

    # 3. Registrar ítems del detalle
    for item in payload.detalles:
        producto = db.query(Producto).filter(
            Producto.id_producto == item.id_producto
        ).first()

        if not producto.disponible:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El producto '{producto.nombre}' no está disponible."
            )

        subtotal_item = producto.precio * item.cantidad_pedida
        monto_total += subtotal_item

        detalle = DetallePedido(
            id_pedido=nuevo_pedido.id_pedido,
            id_producto=item.id_producto,
            cantidad_pedida=item.cantidad_pedida,
            sub_total=subtotal_item
        )
        db.add(detalle)

    # 4. Actualizar total del pedido
    nuevo_pedido.total_pago = monto_total
    db.commit()
    db.refresh(nuevo_pedido)
    return nuevo_pedido


# ─── GET /pedidos/{id} ────────────────────────────────────────────────────────
@router.get("/{id_pedido}", response_model=PedidoResponse)
def obtener_pedido(id_pedido: int, db: Session = Depends(get_db)):
    """HU05: Consulta el estado y detalle de un pedido por su ID."""
    pedido = db.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El pedido con ID {id_pedido} no existe."
        )
    return pedido

# ─── PATCH /pedidos/{id}/estado (NUEVO SPRINT 2) ──────────────────────────────
@router.patch("/{id_pedido}/estado", response_model=PedidoResponse)
def actualizar_estado_pedido(
    id_pedido: int,
    payload: PedidoEstadoUpdate,
    db: Session = Depends(get_db)
):
    """
    TA06-2: Actualiza el estado de un pedido en tiempo real.
    Maneja marcas temporales de auditoría en cocina (TA06-3).
    """
    pedido = db.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El pedido con ID {id_pedido} no existe."
        )

    nuevo_estado = payload.estado.lower()

    # Auditoría de tiempos en cocina (TA06-3)
    if nuevo_estado == "en_preparacion" and pedido.estado == "pendiente":
        pedido.fecha_inicio_prep = datetime.utcnow()
    elif nuevo_estado == "listo" and pedido.estado == "en_preparacion":
        pedido.fecha_fin_prep = datetime.utcnow()

    pedido.estado = nuevo_estado
    db.commit()
    db.refresh(pedido)

    # Notificación vía WebSockets (TA07-3)

    try:
        if manager.active_connections:
            # Bug intencional: se envía solo a la conexión indexada [0]
            asyncio.run(
                manager.send_personal_message(
                    f"Pedido {pedido.id_pedido} cambiado a {pedido.estado}", 
                    manager.active_connections[0]
                )
            )
    except Exception:
        pass

    return pedido