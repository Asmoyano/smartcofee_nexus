import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { getProductos, getCategorias, validarMesaQR } from '../services/api'
import ProductCard from '../components/ProductCard'
import Carrito from '../components/Carrito'

const estilos = {
  contenedor: {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '16px',
    paddingBottom: '80px'
  },
  header: {
    background: '#6B4C2A',
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
    fontSize: '18px'
  },
  btnCarrito: {
    background: '#C4A882',
    color: '#1A1A1A',
    border: 'none',
    borderRadius: '20px',
    padding: '8px 16px',
    fontWeight: '700',
    fontSize: '14px',
    cursor: 'pointer'
  },
  tabs: {
    display: 'flex',
    gap: '8px',
    padding: '12px 16px',
    overflowX: 'auto',
    background: '#fff',
    borderBottom: '1px solid #DDD0C0'
  },
  tab: {
    padding: '6px 16px',
    borderRadius: '20px',
    border: '1px solid #DDD0C0',
    background: '#F5F0EA',
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: '600',
    whiteSpace: 'nowrap',
    color: '#595959'
  },
  tabActivo: {
    padding: '6px 16px',
    borderRadius: '20px',
    border: '1px solid #6B4C2A',
    background: '#6B4C2A',
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: '600',
    whiteSpace: 'nowrap',
    color: '#fff'
  },
  grilla: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
    gap: '16px',
    marginTop: '16px'
  },
  mensajeQR: {
    background: '#FFF3CD',
    border: '1px solid #FFCA2C',
    borderRadius: '10px',
    padding: '12px 16px',
    margin: '12px 0',
    fontSize: '13px',
    color: '#856404',
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  },
  mensajeError: {
    background: '#F8D7DA',
    border: '1px solid #F5C6CB',
    borderRadius: '10px',
    padding: '12px 16px',
    margin: '12px 0',
    fontSize: '13px',
    color: '#721C24'
  },
  confirmacion: {
    textAlign: 'center',
    padding: '40px 20px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '12px'
  },
  iconoOk: {
    fontSize: '56px'
  },
  titConfirmacion: {
    fontWeight: '700',
    fontSize: '22px',
    color: '#1A1A1A'
  },
  subConfirmacion: {
    fontSize: '14px',
    color: '#595959',
    maxWidth: '280px',
    lineHeight: '1.5'
  },
  badgePedido: {
    background: '#6B4C2A',
    color: '#fff',
    borderRadius: '20px',
    padding: '6px 16px',
    fontWeight: '700',
    fontSize: '14px'
  }
}

export default function ClienteView() {
  // HU14 / TA14-1: El qrCode viene directamente desde la URL del QR escaneado
  const { qrCode } = useParams()

  const [mesa, setMesa] = useState(null)
  const [errorMesa, setErrorMesa] = useState(null)
  const [productos, setProductos] = useState([])
  const [categorias, setCategorias] = useState([])
  const [categoriaActiva, setCategoriaActiva] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [carritoAbierto, setCarritoAbierto] = useState(false)
  const [itemsCarrito, setItemsCarrito] = useState([])
  const [pedidoConfirmado, setPedidoConfirmado] = useState(null)

  // HU14 / TA14-1: Al montar el componente, valida el QR antes de mostrar la carta
  useEffect(() => {
    async function inicializar() {
      try {
        const mesaData = await validarMesaQR(qrCode)
        setMesa(mesaData)
      } catch {
        setErrorMesa('El código QR escaneado no es válido o la mesa no existe.')
        setCargando(false)
        return
      }

      try {
        const [cats, prods] = await Promise.all([getCategorias(), getProductos()])
        setCategorias(cats)
        setProductos(prods)
      } catch {
        setErrorMesa('Error al cargar la carta. Intenta de nuevo.')
      } finally {
        setCargando(false)
      }
    }

    inicializar()
  }, [qrCode])

  // Filtra productos por categoría activa
  const productosFiltrados = categoriaActiva
    ? productos.filter(p => p.id_categoria === categoriaActiva)
    : productos

  function agregarAlCarrito(producto) {
    setItemsCarrito(prev => {
      const existente = prev.find(i => i.id_producto === producto.id_producto)
      if (existente) {
        return prev.map(i =>
          i.id_producto === producto.id_producto
            ? { ...i, cantidad: i.cantidad + 1 }
            : i
        )
      }
      return [...prev, { ...producto, cantidad: 1 }]
    })
  }

  function cambiarCantidad(idProducto, nuevaCantidad) {
    if (nuevaCantidad <= 0) {
      setItemsCarrito(prev => prev.filter(i => i.id_producto !== idProducto))
    } else {
      setItemsCarrito(prev =>
        prev.map(i =>
          i.id_producto === idProducto ? { ...i, cantidad: nuevaCantidad } : i
        )
      )
    }
  }

  const totalItems = itemsCarrito.reduce((acc, i) => acc + i.cantidad, 0)

  // Pantalla de confirmación de pedido exitoso
  if (pedidoConfirmado) {
    return (
      <div>
        <div style={estilos.header}>
          <span style={estilos.logo}>☕ SmartCoffee Nexus</span>
        </div>
        <div style={estilos.confirmacion}>
          <span style={estilos.iconoOk}>✅</span>
          <span style={estilos.titConfirmacion}>¡Pedido recibido!</span>
          <span style={estilos.badgePedido}>Pedido #{pedidoConfirmado.id_pedido}</span>
          <p style={estilos.subConfirmacion}>
            Tu pedido ha sido enviado a cocina. Puedes seguir el estado desde esta pantalla.
          </p>
          <p style={{ fontSize: '13px', color: '#595959' }}>
            Mesa: <strong>{qrCode}</strong>
          </p>
          <p style={{ fontSize: '13px', color: '#595959' }}>
            Total: <strong>S/ {pedidoConfirmado.total_pago.toFixed(2)}</strong>
          </p>
        </div>
      </div>
    )
  }

  return (
    <div>
      {/* Header con botón de carrito */}
      <div style={estilos.header}>
        <span style={estilos.logo}>☕ SmartCoffee Nexus</span>
        <button
          style={estilos.btnCarrito}
          onClick={() => setCarritoAbierto(true)}
        >
          🛒 {totalItems > 0 ? `(${totalItems})` : 'Carrito'}
        </button>
      </div>

      <div style={estilos.contenedor}>
        {/* Mensaje de validación de mesa */}
        {mesa && (
          <div style={estilos.mensajeQR}>
            📍 Mesa validada: <strong>{qrCode}</strong> — Tu pedido se vinculará automáticamente.
          </div>
        )}

        {errorMesa && (
          <div style={estilos.mensajeError}>⚠️ {errorMesa}</div>
        )}

        {cargando && <p style={{ color: '#595959', marginTop: '20px' }}>Cargando carta...</p>}

        {!cargando && mesa && (
          <>
            {/* Tabs de categorías */}
            <div style={estilos.tabs}>
              <button
                style={categoriaActiva === null ? estilos.tabActivo : estilos.tab}
                onClick={() => setCategoriaActiva(null)}
              >
                Todos
              </button>
              {categorias.map(cat => (
                <button
                  key={cat.id_categoria}
                  style={cat.id_categoria === categoriaActiva ? estilos.tabActivo : estilos.tab}
                  onClick={() => setCategoriaActiva(cat.id_categoria)}
                >
                  {cat.nombre}
                </button>
              ))}
            </div>

            {/* Grilla de productos */}
            <div style={estilos.grilla}>
              {productosFiltrados.map(producto => (
                <ProductCard
                  key={producto.id_producto}
                  producto={producto}
                  onAgregar={agregarAlCarrito}
                />
              ))}
            </div>

            {productosFiltrados.length === 0 && (
              <p style={{ color: '#595959', marginTop: '20px', textAlign: 'center' }}>
                No hay productos en esta categoría.
              </p>
            )}
          </>
        )}
      </div>

      {/* Carrito lateral */}
      {carritoAbierto && (
        <Carrito
          items={itemsCarrito}
          idMesa={mesa?.id_mesa}
          qrCode={qrCode}
          onCambiarCantidad={cambiarCantidad}
          onCerrar={() => setCarritoAbierto(false)}
          onPedidoConfirmado={(pedido) => {
            setPedidoConfirmado(pedido)
            setCarritoAbierto(false)
            setItemsCarrito([])
          }}
        />
      )}
    </div>
  )
}