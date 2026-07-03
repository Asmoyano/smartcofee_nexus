// Dirección base del backend FastAPI
// Cambia la IP según tu red local si es necesario [http://10.148.251.77:8000, http://192.168.18.54:8000]
const BASE_URL = 'http://10.148.251.229:8000';

// ─── PRODUCTOS ────────────────────────────────────────────────────────────────

/**
 * HU01: Obtiene la lista de productos disponibles.
 * Opcionalmente filtra por categoría.
 * NOTA: Este endpoint contiene el Bug #003 — es_alergeno siempre llega como false.
 */
export async function getProductos(categoriaId = null) {
  const url = categoriaId
    ? `${BASE_URL}/productos?categoria_id=${categoriaId}`
    : `${BASE_URL}/productos`
  const res = await fetch(url)
  if (!res.ok) throw new Error('Error al cargar productos')
  return res.json()
}

/**
 * HU01 / TA02-2: Obtiene el detalle de un producto incluyendo sus insumos y alérgenos.
 * Este endpoint SÍ calcula correctamente es_alergeno vía JOIN Receta → Insumo.
 */
export async function getProductoDetalle(idProducto) {
  const res = await fetch(`${BASE_URL}/productos/${idProducto}`)
  if (!res.ok) throw new Error('Producto no encontrado')
  return res.json()
}

/**
 * TA01-2: Obtiene la lista de categorías para las pestañas del catálogo.
 */
export async function getCategorias() {
  const res = await fetch(`${BASE_URL}/productos/categorias`)
  if (!res.ok) throw new Error('Error al cargar categorías')
  return res.json()
}

/**
 * TA01-2: Crea un nuevo producto (panel de administración).
 */
export async function crearProducto(datos) {
  const res = await fetch(`${BASE_URL}/productos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos)
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Error al crear producto')
  }
  return res.json()
}

/**
 * TA01-2: Actualiza un producto existente (panel de administración).
 */
export async function actualizarProducto(idProducto, datos) {
  const res = await fetch(`${BASE_URL}/productos/${idProducto}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos)
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Error al actualizar producto')
  }
  return res.json()
}

// ─── MESAS ────────────────────────────────────────────────────────────────────

/**
 * HU14 / TA14-1: Valida que el código QR escaneado corresponda a una mesa real.
 */
export async function validarMesaQR(qrCode) {
  const res = await fetch(`${BASE_URL}/mesas/${qrCode}`)
  if (!res.ok) throw new Error('Código QR inválido. La mesa no existe.')
  return res.json()
}

// ─── PEDIDOS ──────────────────────────────────────────────────────────────────

/**
 * HU05 / TA14-3: Crea un pedido vinculando los productos seleccionados a la mesa.
 */
export async function crearPedido(payload) {
  const res = await fetch(`${BASE_URL}/pedidos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Error al crear pedido')
  }
  return res.json()
}

/**
 * HU05: Consulta el estado actual de un pedido por su ID.
 */
export async function getPedido(idPedido) {
  const res = await fetch(`${BASE_URL}/pedidos/${idPedido}`)
  if (!res.ok) throw new Error('Pedido no encontrado')
  return res.json()
}

/**
 * TA05-2: Lista todos los pedidos ordenados por FIFO (más antiguo primero).
 * Opcionalmente filtra por estado.
 */
export async function getPedidos(estado = null) {
  const url = estado
    ? `${BASE_URL}/pedidos?estado=${estado}`
    : `${BASE_URL}/pedidos`
  const res = await fetch(url)
  if (!res.ok) throw new Error('Error al cargar pedidos')
  return res.json()
}