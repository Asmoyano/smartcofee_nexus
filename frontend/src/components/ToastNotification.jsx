import { useState, useEffect } from 'react'
import { WS_URL } from '../services/api'

const estilos = {
  contenedorFlotante: {
    position: 'fixed',
    bottom: '24px',
    right: '24px',
    zIndex: 2000,
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    maxWidth: '360px',
    width: '100%'
  },
  toastCard: {
    background: '#FFF3CD', // Fondo amarillo de advertencia
    border: '1px solid #FFCA2C',
    borderRadius: '10px',
    padding: '16px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: '12px',
    animation: 'slideIn 0.2s ease-out'
  },
  contenido: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px'
  },
  titulo: {
    fontWeight: '700',
    fontSize: '14px',
    color: '#856404',
    display: 'flex',
    alignItems: 'center',
    gap: '6px'
  },
  descripcion: {
    fontSize: '13px',
    color: '#66511A',
    lineHeight: '1.4'
  },
  btnCerrar: {
    background: 'transparent',
    border: 'none',
    color: '#856404',
    fontSize: '16px',
    fontWeight: '700',
    cursor: 'pointer',
    padding: '0 4px',
    lineHeight: 1
  }
}

export default function ToastNotification() {
  const [alertas, setAlertas] = useState([])

  useEffect(() => {
    // Escucha en tiempo real el canal de eventos (TA10-2)
    const ws = new WebSocket(`${WS_URL}/ws`)

    ws.onmessage = (event) => {
      try {
        // Validamos si el mensaje de texto directo del WebSocket es una alerta de stock
        const mensaje = event.data
        
        if (typeof mensaje === 'string' && mensaje.includes('Alerta Crítica')) {
          const nuevaAlerta = {
            id: Date.now(),
            texto: mensaje
          }

          // Agregamos la alerta al feed visual
          setAlertas(prev => [...prev, nuevaAlerta])

          // Auto-ocultar la alerta después de 5 segundos
          setTimeout(() => {
            eliminarAlerta(nuevaAlerta.id)
          }, 5000)
        }
      } catch (err) {
        console.error("Error procesando evento de inventario en el Toast", err)
      }
    }

    return () => ws.close()
  }, [])

  function eliminarAlerta(id) {
    setAlertas(prev => prev.filter(alerta => alerta.id !== id))
  }

  if (alertas.length === 0) return null

  return (
    <div style={estilos.contenedorFlotante}>
      {alertas.map((alerta) => (
        <div key={alerta.id} style={estilos.toastCard}>
          <div style={estilos.contenido}>
            <span style={estilos.titulo}>⚠️ ALERTA DE STOCK</span>
            <span style={estilos.descripcion}>{alerta.texto}</span>
          </div>
          <button 
            style={estilos.btnCerrar} 
            onClick={() => eliminarAlerta(alerta.id)}
          >
            ×
          </button>
        </div>
      ))}
    </div>
  )
}