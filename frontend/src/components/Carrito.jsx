import { crearPedido } from '../services/api'

const estilos = {
  panel: {
    position: 'fixed',
    top: 0,
    right: 0,
    height: '100vh',
    width: '300px',
    background: '#fff',
    boxShadow: '-4px 0 16px rgba(0,0,0,0.12)',
    display: 'flex',
    flexDirection: 'column',
    zIndex: 50,
    transform: 'translateX(0)',
    transition: 'transform 0.3s ease'
  },
  header: {
    background: '#6B4C2A',
    color: '#fff',
    padding: '16px 20px',
    fontWeight: '700',
    fontSize: '16px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  btnCerrar: {
    background: 'transparent',
    border: 'none',
    color: '#fff',
    fontSize: '20px',
    cursor: 'pointer'
  },
  lista: {
    flex: 1,
    overflowY: 'auto',
    padding: '16px'
  },
  itemCarrito: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '10px 0',
    borderBottom: '1px solid #F5F0EA'
  },
  nombreItem: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#1A1A1A'
  },
  controles: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  },
  btnCantidad: {
    width: '26px',
    height: '26px',
    borderRadius: '50%',
    border: '1px solid #DDD0C0',
    background: '#F5F0EA',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '700',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  cantidad: {
    fontSize: '14px',
    fontWeight: '600',
    minWidth: '20px',
    textAlign: 'center'
  },
  subtotal: {
    fontSize: '13px',
    color: '#6B4C2A',
    fontWeight: '600'
  },
  footer: {
    padding: '16px 20px',
    borderTop: '2px solid #F5F0EA'
  },
  totalFila: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '12px'
  },
  totalLabel: {
    fontWeight: '700',
    fontSize: '15px'
  },
  totalValor: {
    fontWeight: '700',
    fontSize: '15px',
    color: '#6B4C2A'
  },
  btnPedir: {
    width: '100%',
    background: '#6B4C2A',
    color: '#fff',
    border: 'none',
    borderRadius: '10px',
    padding: '12px',
    fontSize: '15px',
    fontWeight: '700',
    cursor: 'pointer'
  },
  btnPedirDeshabilitado: {
    width: '100%',
    background: '#DDD0C0',
    color: '#595959',
    border: 'none',
    borderRadius: '10px',
    padding: '12px',
    fontSize: '15px',
    fontWeight: '700',
    cursor: 'not-allowed'
  },
  vacio: {
    textAlign: 'center',
    color: '#595959',
    fontSize: '14px',
    marginTop: '40px'
  },
  mesaTag: {
    background: '#F5F0EA',
    borderRadius: '8px',
    padding: '8px 12px',
    fontSize: '13px',
    color: '#595959',
    marginBottom: '12px',
    textAlign: 'center'
  }
}

export default function Carrito({
  items,
  idMesa,
  qrCode,
  onCambiarCantidad,
  onCerrar,
  onPedidoConfirmado
}) {
  const total = items.reduce((acc, item) => acc + item.precio * item.cantidad, 0)
  const totalItems = items.reduce((acc, item) => acc + item.cantidad, 0)

  /**
   * HU05 / TA14-3: Confirma el pedido enviando los items seleccionados
   * vinculados al id_mesa de la mesa escaneada por QR.
   * TA14-4: El backend recibirá el id_mesa y lo asociará al pedido.
   */
  async function confirmarPedido() {
    if (items.length === 0) return

    const payload = {
      id_mesa: idMesa,
      id_cliente: null,
      id_usuario: null,
      detalles: items.map(item => ({
        id_producto: item.id_producto,
        cantidad_pedida: item.cantidad
      }))
    }

    try {
      const pedido = await crearPedido(payload)
      onPedidoConfirmado(pedido)
    } catch (err) {
      alert(`Error al confirmar el pedido: ${err.message}`)
    }
  }

  return (
    <div style={estilos.panel}>
      <div style={estilos.header}>
        <span>🛒 Tu pedido ({totalItems})</span>
        <button style={estilos.btnCerrar} onClick={onCerrar}>✕</button>
      </div>

      <div style={estilos.lista}>
        {/* TA14-3: Muestra la mesa asociada al QR escaneado */}
        {qrCode && (
          <div style={estilos.mesaTag}>
            📍 Mesa: <strong>{qrCode}</strong>
          </div>
        )}

        {items.length === 0 && (
          <p style={estilos.vacio}>Tu carrito está vacío.<br />Agrega productos de la carta.</p>
        )}

        {items.map(item => (
          <div key={item.id_producto} style={estilos.itemCarrito}>
            <div>
              <div style={estilos.nombreItem}>{item.nombre}</div>
              <div style={estilos.subtotal}>
                S/ {(item.precio * item.cantidad).toFixed(2)}
              </div>
            </div>
            <div style={estilos.controles}>
              <button
                style={estilos.btnCantidad}
                onClick={() => onCambiarCantidad(item.id_producto, item.cantidad - 1)}
              >−</button>
              <span style={estilos.cantidad}>{item.cantidad}</span>
              <button
                style={estilos.btnCantidad}
                onClick={() => onCambiarCantidad(item.id_producto, item.cantidad + 1)}
              >+</button>
            </div>
          </div>
        ))}
      </div>

      <div style={estilos.footer}>
        <div style={estilos.totalFila}>
          <span style={estilos.totalLabel}>Total</span>
          <span style={estilos.totalValor}>S/ {total.toFixed(2)}</span>
        </div>
        <button
          style={items.length > 0 ? estilos.btnPedir : estilos.btnPedirDeshabilitado}
          onClick={confirmarPedido}
          disabled={items.length === 0}
        >
          Confirmar pedido
        </button>
      </div>
    </div>
  )
}