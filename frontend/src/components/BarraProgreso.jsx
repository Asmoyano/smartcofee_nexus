import { useState, useEffect } from 'react'
import { getPedido, getTiempoEsperaEstimado, WS_URL } from '../services/api'

const estilos = {
  contenedor: {
    background: '#FFFFFF',
    borderRadius: '16px',
    padding: '20px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.06)',
    border: '1px solid #DDD0C0',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
    marginTop: '16px'
  },
  tituloFila: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  textoPedido: {
    fontWeight: '700',
    fontSize: '16px',
    color: '#1A1A1A'
  },
  tiempoEstimado: {
    fontSize: '13px',
    color: '#6B4C2A',
    fontWeight: '600',
    background: '#F5F0EA',
    padding: '4px 10px',
    borderRadius: '8px'
  },
  rielProgreso: {
    height: '10px',
    background: '#EFEBE6',
    borderRadius: '20px',
    position: 'relative',
    overflow: 'hidden',
    margin: '10px 0'
  },
  barraActiva: {
    height: '100%',
    background: '#6B4C2A',
    borderRadius: '20px',
    transition: 'width 0.4s ease-out'
  },
  pasosContenedor: {
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: '4px'
  },
  pasoItem: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '4px',
    flex: 1,
    textAlign: 'center'
  },
  nodoCirculo: {
    width: '12px',
    height: '12px',
    borderRadius: '50%',
    transition: 'background 0.3s, transform 0.3s'
  },
  pasoTexto: {
    fontSize: '12px',
    fontWeight: '600'
  }
}

// Mapeo analítico de porcentajes de carga para el riel visual
function calcularPorcentaje(estado) {
  switch (estado) {
    case 'pendiente': return 15
    case 'en_preparacion': return 50
    case 'listo': return 85
    case 'entregado': return 100
    case 'cancelado': return 0
    default: return 0
  }
}

export default function BarraProgreso({ idPedido }) {
  const [estadoActual, setEstadoActual] = useState('pendiente')
  const [tiempoMinutos, setTiempoMinutos] = useState(null)
  const [error, setError] = useState(false)

  // TA07-1 & HU05: Sincroniza datos del pedido y el estimado analítico de espera
  async function sincronizarProgreso() {
    try {
      const [pedidoData, tiempoData] = await Promise.all([
        getPedido(idPedido),
        getTiempoEsperaEstimado()
      ])
      setEstadoActual(pedidoData.estado)
      setTiempoMinutos(tiempoData.tiempo_estimado_minutos)
    } catch {
      setError(true)
    }
  }

  useEffect(() => {
    sincronizarProgreso()

    // TA07-3: Canal WebSocket reactivo para mutaciones de estado en tiempo real
    const ws = new WebSocket(`${WS_URL}/ws`)

    ws.onmessage = (event) => {
      // Al recibir la señal de cocina, refresca automáticamente el estado sin intervención manual
      sincronizarProgreso()
    }

    return () => ws.close()
  }, [idPedido])

  if (error) return null

  const porcentaje = calcularPorcentaje(estadoActual)
  const esCancelado = estadoActual === 'cancelado'

  return (
    <div style={estilos.contenedor}>
      {/* Encabezado del Progreso */}
      <div style={estilos.tituloFila}>
        <span style={estilos.textoPedido}>
          Estado: {esCancelado ? '❌ Cancelado' : `⏱️ ${estadoActual.toUpperCase().replace('_', ' ')}`}
        </span>
        {tiempoMinutos && !['listo', 'entregado', 'cancelado'].includes(estadoActual) && (
          <span style={estilos.tiempoEstimado}>
            Espera: ~{tiempoMinutos} min
          </span>
        )}
      </div>

      {/* Riel Visual Reactivo */}
      <div style={estilos.rielProgreso}>
        <div 
          style={{ 
            ...estilos.barraActiva, 
            width: `${porcentaje}%`,
            background: esCancelado ? '#DC3545' : '#6B4C2A'
          }} 
        />
      </div>

      {/* Nodos de Control de Pasos */}
      {!esCancelado && (
        <div style={estilos.pasosContenedor}>
          {[
            { clave: 'pendiente', label: 'Recibido' },
            { clave: 'en_preparacion', label: 'En Cocina' },
            { clave: 'listo', label: '¡Listo!' },
            { clave: 'entregado', label: 'Entregado' }
          ].map((paso) => {
            const pasosLista = ['pendiente', 'en_preparacion', 'listo', 'entregado']
            const indiceActual = pasosLista.indexOf(estadoActual)
            const indicePaso = pasosLista.indexOf(paso.clave)
            const completado = indicePaso <= indiceActual

            return (
              <div key={paso.clave} style={estilos.pasoItem}>
                <div 
                  style={{ 
                    ...estilos.nodoCirculo, 
                    background: completado ? '#6B4C2A' : '#EFEBE6',
                    transform: paso.clave === estadoActual ? 'scale(1.3)' : 'none'
                  }} 
                />
                <span 
                  style={{ 
                    ...estilos.pasoTexto, 
                    color: completado ? '#1A1A1A' : '#A6A6A6' 
                  }}
                >
                  {paso.label}
                </span>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}