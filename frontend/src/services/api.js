// La URL del backend se lee desde la variable de entorno.
// En local usa el .env.local, en Vercel usa la variable configurada en el dashboard.
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
export const WS_URL = BASE_URL.replace(/^http/, 'ws')

// ─── PRODUCTOS ───────────────────────────────────────────────────────────────
export async function getProductos(categoriaId = null) {
  const url = categoriaId
    ? `${BASE_URL}/productos?categoria_id=${categoriaId}`
    : `${BASE_URL}/productos`
  const res = await fetch(url)
  if (!res.ok) throw new Error('Error al cargar productos')
  return res.json()
}

export async function getProductoDetalle(idProducto) {
  const res = await fetch(`${BASE_URL}/productos/${idProducto}`)
  if (!res.ok) throw new Error('Producto no encontrado')
  return res.json()
}

export async function getCategorias() {
  const res = await fetch(`${BASE_URL}/productos/categorias`)
  if (!res.ok) throw new Error('Error al cargar categorías')
  return res.json()
}

export async function crearProducto(datos) {
  const res = await fetch(`${BASE_URL}/productos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos)
  })
  if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Error al crear producto') }
  return res.json()
}

export async function actualizarProducto(idProducto, datos) {
  const res = await fetch(`${BASE_URL}/productos/${idProducto}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos)
  })
  if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Error al actualizar') }
  return res.json()
}

// ─── MESAS ────────────────────────────────────────────────────────────────────
export async function validarMesaQR(qrCode) {
  const res = await fetch(`${BASE_URL}/mesas/${qrCode}`)
  if (!res.ok) throw new Error('Código QR inválido. La mesa no existe.')
  return res.json()
}

// ─── PEDIDOS ──────────────────────────────────────────────────────────────────
export async function crearPedido(payload) {
  const res = await fetch(`${BASE_URL}/pedidos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Error al crear pedido') }
  return res.json()
}

export async function getPedido(idPedido) {
  const res = await fetch(`${BASE_URL}/pedidos/${idPedido}`)
  if (!res.ok) throw new Error('Pedido no encontrado')
  return res.json()
}

export async function getPedidos(estado = null) {
  const url = estado
    ? `${BASE_URL}/pedidos?estado=${estado}`
    : `${BASE_URL}/pedidos`
  const res = await fetch(url)
  if (!res.ok) throw new Error('Error al cargar pedidos')
  return res.json()
}

export async function actualizarEstadoPedido(idPedido, nuevoEstado) {
  const res = await fetch(`${BASE_URL}/pedidos/${idPedido}/estado`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ estado: nuevoEstado })
  })
  if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Error al actualizar estado') }
  return res.json()
}

// ─── INVENTARIO ───────────────────────────────────────────────────────────────
export async function getInventario() {
  const res = await fetch(`${BASE_URL}/inventario`)
  if (!res.ok) throw new Error('Error al cargar inventario')
  return res.json()
}

export async function getAlertasStock() {
  const res = await fetch(`${BASE_URL}/inventario/alertas`)
  if (!res.ok) throw new Error('Error al cargar alertas')
  return res.json()
}

export async function getTiempoEsperaEstimado() {
  const res = await fetch(`${BASE_URL}/inventario/tiempo-espera-estimado`)
  if (!res.ok) throw new Error('Error al obtener tiempo estimado')
  return res.json()
}

export async function actualizarInsumo(idInsumo, datos) {
  const res = await fetch(`${BASE_URL}/inventario/${idInsumo}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos)
  })
  if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Error al actualizar insumo') }
  return res.json()
}

export async function crearInsumo(datosInsumo) {
  const res = await fetch(`${BASE_URL}/inventario/insumos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datosInsumo)
  })
  if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Error al crear insumo') }
  return res.json()
}

export async function descontarStockPorPedido(idPedido) {
  const res = await fetch(`${BASE_URL}/inventario/descontar-pedido/${idPedido}`, {
    method: 'POST'
  })
  if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Error al descontar stock') }
  return res.json()
}

// ─── WEBSOCKET ────────────────────────────────────────────────────────────────
export function crearWebSocketPedido(idPedido, onMensaje) {
  const ws = new WebSocket(`${WS_URL}/pedidos/ws/${idPedido}`)
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      onMensaje(data)
    } catch {
      console.warn('WS mensaje no JSON:', event.data)
    }
  }
  ws.onerror = (err) => console.error('WS error:', err)
  return ws
}
