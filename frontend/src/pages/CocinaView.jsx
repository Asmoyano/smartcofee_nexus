import { useState, useEffect } from 'react'
import { getPedidos, actualizarEstadoPedido, descontarStockPorPedido, WS_URL } from '../services/api'

const estilos = {
  header: {
    background: '#1A1A1A', // Color oscuro industrial para cocina
    color: '#fff',
    padding: '16px 20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    position: 'sticky',
    top: 0,
    zIndex: 40
  },
  logo: {
    fontWeight: '700',
    fontSize: '18px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  },
  badgeOnline: {
    background: '#198754',
    color: '#fff',
    padding: '4px 10px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: '600'
  },
  contenedor: {
    padding: '20px',
    maxWidth: '1400px',
    margin: '0 auto'
  },
  seccionTitulo: {
    fontSize: '20px',
    fontWeight: '700',
    color: '#1A1A1A',
    marginBottom: '16px',
    borderBottom: '2px solid #E0E0E0',
    paddingBottom: '8px'
  },
  grillaMonitor: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '20px',
    alignItems: 'start'
  },
  tarjetaComanda: {
    background: '#FFF',
    border: '1px solid #DDD0C0',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.05)',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden'
  },
  comandaHeader: {
    padding: '12px 16px',
    color: '#FFF',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    fontWeight: '700'
  },
  comandaCuerpo: {
    padding: '16px',
    flexGrow: 1
  },
  itemLinea: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '8px 0',
    borderBottom: '1px dashed #E0E0E0',
    fontSize: '14px',
    color: '#333'
  },
  comandaFooter: {
    padding: '12px 16px',
    background: '#F9F6F0',
    borderTop: '1px solid #DDD0C0',
    display: 'flex',
    gap: '10px'
  },
  btnAccion: {
    flex: 1,
    padding: '10px',
    border: 'none',
    borderRadius: '8px',
    fontWeight: '700',
    fontSize: '13px',
    cursor: 'pointer',
    textAlign: 'center',
    transition: 'background 0.2s'
  },
  mensajeError: {
    background: '#F8D7DA',
    border: '1px solid #F5C6CB',
    borderRadius: '10px',
    padding: '12px 16px',
    margin: '12px 0',
    fontSize: '13px',
    color: '#721C24'
  }
}

// Colores dinámicos según el estado del pedido FIFO
function obtenerColorEstado(estado) {
  switch (estado) {
    case 'pendiente': return '#DC3545'      // Rojo - Requiere atención inmediata
    case 'en_preparacion': return '#0D6EFD' // Azul - En proceso
    default: return '#6C757D'
  }
}

export default function CocinaView() {
  const [pedidos, setPedidos] = useState([])
  const [error, setError] = useState(null)
  const [cargando, setCargando] = useState(true)

  // 1. Carga inicial de pedidos activos en cocina (Pendientes y En Preparación)
  async function cargarPedidosCocina() {
    try {
      // Cargamos por separado para asegurar la visualización estricta de la cola de trabajo activa
      const [pendientes, enPrep] = await Promise.all([
        getPedidos('pendiente'),
        getPedidos('en_preparacion')
      ])
      // Combinamos manteniendo el orden FIFO (más antiguos primero)
      const colaActiva = [...pendientes, ...enPrep].sort(
        (a, b) => a.id_pedido - b.id_pedido
      )
      setPedidos(colaActiva)
    } catch (err) {
      setError('Error al sincronizar la cola de comandas.')
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargarPedidosCocina()

    // 2. TA07-3: Conexión WebSocket para recibir alertas en Tiempo Real
    const ws = new WebSocket(`${WS_URL}/ws`)

    ws.onmessage = (event) => {
      // Cuando entra una actualización (Ej: un cliente crea un pedido nuevo o cambia un estado),
      // refrescamos el monitor automáticamente sin obligar al cocinero a presionar F5
      cargarPedidosCocina()
    }

    ws.onerror = () => {
      console.error('Error en la conexión del WebSocket de Cocina')
    }

    return () => ws.close() // Limpieza de la sesión al desmontar
  }, [])

  // 3. TA06-1: Botones de Acción Interactiva para mutar estados
  async function avanzarEstado(idPedido, estadoActual) {
    try {
      setError(null)
      if (estadoActual === 'pendiente') {
        // Pasa a producción
        await actualizarEstadoPedido(idPedido, 'en_preparacion')
      } else if (estadoActual === 'en_preparacion') {
        // TA09-2: Dispara primero el descuento atómico de inventario basado en recetas
        await descontarStockPorPedido(idPedido)
        // Si el inventario no tira error por stock crítico, pasa a "Listo"
        await actualizarEstadoPedido(idPedido, 'listo')
      }
      // Actualizamos la vista local
      await cargarPedidosCocina()
    } catch (err) {
      // Captura los mensajes de error del backend (¡Aquí se reflejarán los Bugs #001 y #005!)
      setError(err.message)
    }
  }

  return (
    <div style={{ background: '#F4F4F4', minHeight: '100vh' }}>
      {/* Navbar de Control Industrial */}
      <div style={estilos.header}>
        <span style={estilos.logo}>🧑‍🍳 Monitor de Cocina — SmartCoffee</span>
        <span style={estilos.badgeOnline}>● TIEMPO REAL ACTIVO</span>
      </div>

      <div style={estilos.contenedor}>
        <h2 style={estilos.seccionTitulo}>Comandas en Cola (Orden FIFO)</h2>

        {error && <div style={estilos.mensajeError}>⚠️ {error}</div>}
        {cargando && <p style={{ color: '#666' }}>Sincronizando monitor...</p>}

        {!cargando && pedidos.length === 0 && (
          <p style={{ textAlign: 'center', color: '#666', marginTop: '40px', fontSize: '16px' }}>
            🎉 ¡Felicidades! No hay pedidos pendientes de preparación en este momento.
          </p>
        )}

        {/* Monitor Dinámico de Tarjetas */}
        <div style={estilos.grillaMonitor}>
          {pedidos.map((pedido) => (
            <div key={pedido.id_pedido} style={estilos.tarjetaComanda}>
              {/* Encabezado con color reactivo al estado de urgencia */}
              <div style={{ ...estilos.comandaHeader, background: obtenerColorEstado(pedido.estado) }}>
                <span>Orden #{pedido.id_pedido}</span>
                <span>Mesa {pedido.id_mesa}</span>
              </div>

              {/* Cuerpo detallando cantidades e ítems */}
              <div style={estilos.comandaCuerpo}>
                <p style={{ fontSize: '12px', color: '#777', marginBottom: '8px' }}>
                  Recibido: {new Date(pedido.fecha_creacion).toLocaleTimeString()}
                </p>
                {pedido.detalles.map((item, idx) => (
                  <div key={idx} style={estilos.itemLinea}>
                    <span><strong>{item.cantidad_pedida}x</strong> {item.producto.nombre}</span>
                  </div>
                ))}
              </div>

              {/* Footer con botones de control interactivo (TA06-1) */}
              <div style={estilos.comandaFooter}>
                {pedido.estado === 'pendiente' ? (
                  <button
                    style={{ ...estilos.btnAccion, background: '#0D6EFD', color: '#FFF' }}
                    onClick={() => avanzarEstado(pedido.id_pedido, pedido.estado)}
                  >
                    👨‍🍳 Empezar Preparación
                  </button>
                ) : (
                  <button
                    style={{ ...estilos.btnAccion, background: '#198754', color: '#FFF' }}
                    onClick={() => avanzarEstado(pedido.id_pedido, pedido.estado)}
                  >
                    ✅ Marcar como Listo
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}