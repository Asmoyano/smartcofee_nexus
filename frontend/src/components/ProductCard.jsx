import { useState } from 'react'
import AlergenoIcon from './AlergenoIcon'
import { getProductoDetalle } from '../services/api'

const estilos = {
  card: {
    background: '#FFFFFF',
    borderRadius: '12px',
    padding: '16px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    cursor: 'pointer',
    transition: 'transform 0.15s ease, box-shadow 0.15s ease'
  },
  imagen: {
    width: '100%',
    height: '140px',
    objectFit: 'cover',
    borderRadius: '8px',
    background: '#DDD0C0'
  },
  imagenPlaceholder: {
    width: '100%',
    height: '140px',
    borderRadius: '8px',
    background: '#DDD0C0',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '32px'
  },
  nombre: {
    fontWeight: '700',
    fontSize: '15px',
    color: '#1A1A1A'
  },
  descripcion: {
    fontSize: '13px',
    color: '#595959',
    lineHeight: '1.4'
  },
  precio: {
    fontWeight: '700',
    fontSize: '16px',
    color: '#6B4C2A'
  },
  fila: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: '4px'
  },
  btnAgregar: {
    background: '#6B4C2A',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    padding: '6px 14px',
    fontSize: '13px',
    fontWeight: '600',
    cursor: 'pointer'
  },
  modal: {
    position: 'fixed',
    inset: 0,
    background: 'rgba(0,0,0,0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 100,
    padding: '16px'
  },
  modalContenido: {
    background: '#fff',
    borderRadius: '16px',
    padding: '24px',
    maxWidth: '420px',
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px'
  },
  modalTitulo: {
    fontWeight: '700',
    fontSize: '18px',
    color: '#1A1A1A'
  },
  insumoTag: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '4px',
    background: '#F5F0EA',
    borderRadius: '8px',
    padding: '4px 10px',
    fontSize: '12px',
    color: '#595959',
    margin: '2px'
  },
  btnCerrar: {
    background: 'transparent',
    border: '1px solid #DDD0C0',
    borderRadius: '8px',
    padding: '8px',
    cursor: 'pointer',
    color: '#595959',
    fontSize: '13px'
  }
}

export default function ProductCard({ producto, onAgregar }) {
  const [modalAbierto, setModalAbierto] = useState(false)
  const [detalle, setDetalle] = useState(null)
  const [cargando, setCargando] = useState(false)

  /**
   * HU01: Al hacer clic en la tarjeta se carga el detalle completo del producto.
   * HU02 / TA02-2: El detalle incluye los insumos con es_alergeno correcto
   * porque usa GET /productos/{id} que sí hace el JOIN.
   */
  async function abrirDetalle() {
    setModalAbierto(true)
    if (!detalle) {
      setCargando(true)
      try {
        const data = await getProductoDetalle(producto.id_producto)
        setDetalle(data)
      } catch {
        setDetalle(null)
      } finally {
        setCargando(false)
      }
    }
  }

  function agregarAlCarrito() {
    onAgregar(producto)
    setModalAbierto(false)
  }

  return (
    <>
      <div style={estilos.card} onClick={abrirDetalle}>
        {producto.imagen_url
          ? <img src={producto.imagen_url} alt={producto.nombre} style={estilos.imagen} />
          : <div style={estilos.imagenPlaceholder}>☕</div>
        }
        <span style={estilos.nombre}>{producto.nombre}</span>
        <span style={estilos.descripcion}>{producto.descripcion}</span>

        {/*
          BUG #003 visible: producto.es_alergeno siempre es false aquí
          porque viene del endpoint de lista que no calcula el campo.
          El ícono nunca se renderiza desde la tarjeta de catálogo.
        */}
        <AlergenoIcon visible={producto.es_alergeno} />

        <div style={estilos.fila}>
          <span style={estilos.precio}>S/ {producto.precio.toFixed(2)}</span>
          <button
            style={estilos.btnAgregar}
            onClick={(e) => { e.stopPropagation(); onAgregar(producto) }}
          >
            + Agregar
          </button>
        </div>
      </div>

      {/* Modal de detalle del producto */}
      {modalAbierto && (
        <div style={estilos.modal} onClick={() => setModalAbierto(false)}>
          <div style={estilos.modalContenido} onClick={e => e.stopPropagation()}>
            {cargando && <p style={{ color: '#595959' }}>Cargando detalle...</p>}

            {detalle && (
              <>
                <span style={estilos.modalTitulo}>{detalle.nombre}</span>
                <p style={{ fontSize: '14px', color: '#595959' }}>{detalle.descripcion}</p>
                <span style={estilos.precio}>S/ {detalle.precio.toFixed(2)}</span>

                {/* TA02-3: Ícono de alérgeno en el detalle — aquí SÍ funciona */}
                <AlergenoIcon visible={detalle.es_alergeno} />

                {/* TA02-2: Lista de ingredientes con sus alérgenos */}
                {detalle.insumos && detalle.insumos.length > 0 && (
                  <div>
                    <p style={{ fontSize: '13px', fontWeight: '600', marginBottom: '6px' }}>
                      Ingredientes:
                    </p>
                    <div style={{ display: 'flex', flexWrap: 'wrap' }}>
                      {detalle.insumos.map(ins => (
                        <span key={ins.id_insumo} style={{
                          ...estilos.insumoTag,
                          background: ins.es_alergeno ? '#FFF3CD' : '#F5F0EA',
                          color: ins.es_alergeno ? '#856404' : '#595959',
                          border: ins.es_alergeno ? '1px solid #FFCA2C' : 'none'
                        }}>
                          {ins.es_alergeno ? '⚠️ ' : ''}{ins.nombre}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <button style={estilos.btnAgregar} onClick={agregarAlCarrito}>
                  Agregar al pedido
                </button>
                <button style={estilos.btnCerrar} onClick={() => setModalAbierto(false)}>
                  Cerrar
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </>
  )
}