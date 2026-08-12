from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import Pedido, DetallePedido, Producto, Mesa
from app.schemas import PedidoCreate, PedidoResponse, PedidoEstadoUpdate
from app.websocket_manager import manager

router = APIRouter(prefix="/pedidos", tags=["Pedidos & Órdenes"])

ESTADOS_VALIDOS = ["pendiente", "en_preparacion", "listo", "entregado", "cancelado"]


# ─── WebSocket — HU07 ─────────────────────────────────────────────────────────
@router.websocket("/ws/{pedido_id}")
async def websocket_pedido(websocket: WebSocket, pedido_id: int):
    """
    HU07: Canal WebSocket por pedido.
    El cliente se conecta al confirmar su pedido y recibe
    actualizaciones de estado en tiempo real sin recargar la página.
    """
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ─── GET /pedidos ─────────────────────────────────────────────────────────────
@router.get("", response_model=List[PedidoResponse])
def listar_pedidos(estado: Optional[str] = None, db: Session = Depends(get_db)):
    """Lista pedidos ordenados FIFO. Filtra opcionalmente por estado."""
    query = db.query(Pedido).order_by(Pedido.fecha_creacion.asc())
    if estado:
        if estado not in ESTADOS_VALIDOS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Estado '{estado}' no válido. Use: {', '.join(ESTADOS_VALIDOS)}"
            )
        query = query.filter(Pedido.estado == estado)
    return query.all()


# ─── GET /pedidos/{id} ────────────────────────────────────────────────────────
@router.get("/{id_pedido}", response_model=PedidoResponse)
def obtener_pedido(id_pedido: int, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El pedido con ID {id_pedido} no existe."
        )
    return pedido


# ─── POST /pedidos ────────────────────────────────────────────────────────────
@router.post("", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
def crear_pedido(payload: PedidoCreate, db: Session = Depends(get_db)):
    """HU05: Registra un nuevo pedido vinculado a una mesa."""
    mesa = db.query(Mesa).filter(Mesa.id_mesa == payload.id_mesa).first()
    if not mesa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La mesa con ID {payload.id_mesa} no existe."
        )

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
    for item in payload.detalles:
        producto = db.query(Producto).filter(
            Producto.id_producto == item.id_producto
        ).first()

        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El producto con ID {item.id_producto} no existe."
            )

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

    nuevo_pedido.total_pago = monto_total
    db.commit()
    db.refresh(nuevo_pedido)
    return nuevo_pedido


# ─── PATCH /pedidos/{id}/estado ───────────────────────────────────────────────
@router.patch("/{id_pedido}/estado", response_model=PedidoResponse)
async def actualizar_estado_pedido(
    id_pedido: int,
    payload: PedidoEstadoUpdate,
    db: Session = Depends(get_db)
):
    """
    HU06: Actualiza el estado de un pedido desde el monitor de cocina.
    Registra timestamps de auditoría (TA06-3) y notifica a todos
    los clientes conectados vía WebSocket (HU07).
    """
    nuevo_estado = payload.estado.lower()

    if nuevo_estado not in ESTADOS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Estado '{nuevo_estado}' no válido. Use: {', '.join(ESTADOS_VALIDOS)}"
        )

    pedido = db.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El pedido con ID {id_pedido} no existe."
        )

    # TA06-3: Registrar timestamps de auditoría
    ahora = datetime.utcnow()
    if nuevo_estado == "en_preparacion" and pedido.estado == "pendiente":
        pedido.fecha_inicio_prep = ahora
    elif nuevo_estado == "listo" and pedido.estado == "en_preparacion":
        pedido.fecha_fin_prep = ahora
    elif nuevo_estado == "entregado":
        pedido.fecha_entrega = ahora

    pedido.estado = nuevo_estado
    db.commit()
    db.refresh(pedido)

    # HU07: Notificar a todos los clientes conectados vía WebSocket
    mensaje = f'{{"id_pedido": {id_pedido}, "estado": "{nuevo_estado}"}}'
    await manager.broadcast(mensaje)

    return pedido