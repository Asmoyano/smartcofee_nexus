import { useState, useEffect } from 'react'
import { getProductos, getCategorias, crearProducto, actualizarProducto, crearInsumo } from '../services/api'
import ToastNotification from '../components/ToastNotification' // NUEVO: Monitor de alertas en segundo plano (TA10-2)

const estilos = {
  header: {
    background: '#6B4C2A',
    color: '#fff',
    padding: '16px 24px',
    fontWeight: '700',
    fontSize: '18px'
  },
  pestanasContenedor: {
    display: 'flex',
    gap: '4px',
    background: '#F5F0EA',
    padding: '8px 16px',
    borderBottom: '1px solid #DDD0C0'
  },
  pestanaBtn: {
    padding: '8px 16px',
    border: 'none',
    background: 'transparent',
    fontSize: '14px',
    fontWeight: '600',
    color: '#595959',
    cursor: 'pointer',
    borderRadius: '6px'
  },
  pestanaBtnActiva: {
    padding: '8px 16px',
    border: 'none',
    background: '#6B4C2A',
    fontSize: '14px',
    fontWeight: '700',
    color: '#fff',
    cursor: 'pointer',
    borderRadius: '6px'
  },
  contenedor: {
    maxWidth: '900px',
    margin: '0 auto',
    padding: '24px 16px'
  },
  seccion: {
    background: '#fff',
    borderRadius: '12px',
    padding: '24px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
    marginBottom: '24px'
  },
  titulo: {
    fontWeight: '700',
    fontSize: '16px',
    color: '#1A1A1A',
    marginBottom: '16px',
    borderBottom: '2px solid #F5F0EA',
    paddingBottom: '8px'
  },
  formulario: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '16px'
  },
  campoCompleto: {
    gridColumn: '1 / -1'
  },
  label: {
    display: 'block',
    fontSize: '13px',
    fontWeight: '600',
    color: '#595959',
    marginBottom: '4px'
  },
  input: {
    width: '100%',
    padding: '10px 12px',
    border: '1px solid #DDD0C0',
    borderRadius: '8px',
    fontSize: '14px',
    color: '#1A1A1A',
    background: '#F5F0EA',
    outline: 'none'
  },
  select: {
    width: '100%',
    padding: '10px 12px',
    border: '1px solid #DDD0C0',
    borderRadius: '8px',
    fontSize: '14px',
    color: '#1A1A1A',
    background: '#F5F0EA'
  },
  textarea: {
    width: '100%',
    padding: '10px 12px',
    border: '1px solid #DDD0C0',
    borderRadius: '8px',
    fontSize: '14px',
    color: '#1A1A1A',
    background: '#F5F0EA',
    resize: 'vertical',
    minHeight: '80px'
  },
  checkboxFila: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '14px',
    color: '#1A1A1A'
  },
  botones: {
    display: 'flex',
    gap: '10px',
    marginTop: '8px',
    gridColumn: '1 / -1'
  },
  btnGuardar: {
    background: '#6B4C2A',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    padding: '10px 24px',
    fontWeight: '700',
    fontSize: '14px',
    cursor: 'pointer'
  },
  btnCancelar: {
    background: '#F5F0EA',
    color: '#595959',
    border: '1px solid #DDD0C0',
    borderRadius: '8px',
    padding: '10px 24px',
    fontWeight: '600',
    fontSize: '14px',
    cursor: 'pointer'
  },
  mensajeExito: {
    background: '#D4EDDA',
    border: '1px solid #C3E6CB',
    borderRadius: '8px',
    padding: '10px 16px',
    fontSize: '13px',
    color: '#155724',
    marginBottom: '16px'
  },
  mensajeError: {
    background: '#F8D7DA',
    border: '1px solid #F5C6CB',
    borderRadius: '8px',
    padding: '10px 16px',
    fontSize: '13px',
    color: '#721C24',
    marginBottom: '16px'
  },
  tablaProductos: {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '14px'
  },
  th: {
    textAlign: 'left',
    padding: '10px 12px',
    background: '#F5F0EA',
    fontWeight: '600',
    color: '#595959',
    fontSize: '12px',
    borderBottom: '2px solid #DDD0C0'
  },
  td: {
    padding: '10px 12px',
    borderBottom: '1px solid #F5F0EA',
    color: '#1A1A1A'
  },
  btnEditar: {
    background: '#C4A882',
    color: '#1A1A1A',
    border: 'none',
    borderRadius: '6px',
    padding: '4px 12px',
    fontSize: '12px',
    fontWeight: '600',
    cursor: 'pointer'
  },
  badgeDisponible: {
    background: '#D4EDDA',
    color: '#155724',
    borderRadius: '10px',
    padding: '2px 8px',
    fontSize: '11px',
    fontWeight: '600'
  },
  badgeNoDisponible: {
    background: '#F8D7DA',
    color: '#721C24',
    borderRadius: '10px',
    padding: '2px 8px',
    fontSize: '11px',
    fontWeight: '600'
  }
}

const FORM_INICIAL = {
  nombre: '',
  descripcion: '',
  precio: '',
  imagen_url: '',
  id_categoria: '',
  disponible: true
}

// Estructura limpia para el formulario administrativo de insumos (HU09)
const FORM_INSUMO_INICIAL = {
  nombre: '',
  stock_actual: '',
  stock_minimo: '',
  unidad_medida: 'gr',
  es_alergeno: false
}

export default function AdminView() {
  // Estado para controlar qué sección del panel visualizamos
  const [tabActiva, setTabActiva] = useState('productos') // 'productos' o 'inventario'

  const [categorias, setCategorias] = useState([])
  const [productos, setProductos] = useState([])
  const [form, setForm] = useState(FORM_INICIAL)
  const [editandoId, setEditandoId] = useState(null)
  const [mensaje, setMensaje] = useState(null)
  const [error, setError] = useState(null)
  const [cargando, setCargando] = useState(false)

  // NUEVO SPRINT 2: Estados locales para el subformulario de insumos básicos
  const [formInsumo, setFormInsumo] = useState(FORM_INSUMO_INICIAL)
  const [mensajeInsumo, setMensajeInsumo] = useState(null)
  const [errorInsumo, setErrorInsumo] = useState(null)

  useEffect(() => {
    async function cargar() {
      try {
        const [cats, prods] = await Promise.all([getCategorias(), getProductos()])
        setCategorias(cats)
        setProductos(prods)
      } catch (e) {
        setError('Error al cargar datos del servidor.')
      }
    }
    cargar()
  }, [])

  function manejarCambio(e) {
    const { name, value, type, checked } = e.target
    setForm(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  // Captura el estado del formulario de insumos
  function manejarCambioInsumo(e) {
    const { name, value, type, checked } = e.target
    setFormInsumo(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  function iniciarEdicion(producto) {
    setTabActiva('productos') // Asegurar cambio de pestaña si edita
    setEditandoId(producto.id_producto)
    setForm({
      nombre: producto.nombre,
      descripcion: producto.descripcion || '',
      precio: producto.precio.toString(),
      imagen_url: producto.imagen_url || '',
      id_categoria: producto.id_categoria.toString(),
      disponible: producto.disponible
    })
    setMensaje(null)
    setError(null)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function cancelarEdicion() {
    setEditandoId(null)
    setForm(FORM_INICIAL)
    setMensaje(null)
    setError(null)
  }

  async function manejarEnvio(e) {
    e.preventDefault()
    setMensaje(null)
    setError(null)

    if (!form.nombre.trim()) return setError('El nombre del producto es obligatorio.')
    if (!form.precio || isNaN(form.precio) || parseFloat(form.precio) <= 0)
      return setError('El precio debe ser un número mayor a 0.')
    if (!form.id_categoria) return setError('Debes seleccionar una categoría.')

    setCargando(true)
    const datos = {
      nombre: form.nombre.trim(),
      descripcion: form.descripcion.trim() || null,
      precio: parseFloat(form.precio),
      imagen_url: form.imagen_url.trim() || null,
      id_categoria: parseInt(form.id_categoria),
      disponible: form.disponible
    }

    try {
      if (editandoId) {
        await actualizarProducto(editandoId, datos)
        setMensaje(`Producto "${datos.nombre}" actualizado correctamente.`)
      } else {
        await crearProducto(datos)
        setMensaje(`Producto "${datos.nombre}" creado correctamente.`)
      }

      const prods = await getProductos()
      setProductos(prods)
      cancelarEdicion()
    } catch (err) {
      setError(err.message)
    } finally {
      setCargando(false)
    }
  }

  /**
   * TA09-3: Envía el payload de registro de materia prima al backend.
   */
  async function manejarEnvioInsumo(e) {
    e.preventDefault()
    setMensajeInsumo(null)
    setErrorInsumo(null)

    if (!formInsumo.nombre.trim()) return setErrorInsumo('El nombre del insumo es obligatorio.')
    if (formInsumo.stock_actual === '' || isNaN(formInsumo.stock_actual) || parseFloat(formInsumo.stock_actual) < 0)
      return setErrorInsumo('El stock actual debe ser un número igual o mayor a 0.')
    if (formInsumo.stock_minimo === '' || isNaN(formInsumo.stock_minimo) || parseFloat(formInsumo.stock_minimo) < 0)
      return setErrorInsumo('El stock mínimo de alerta debe ser igual o mayor a 0.')

    setCargando(true)
    const datosInsumo = {
      nombre: formInsumo.nombre.trim(),
      stock_actual: parseFloat(formInsumo.stock_actual),
      stock_minimo: parseFloat(formInsumo.stock_minimo),
      unidad_medida: formInsumo.unidad_medida,
      es_alergeno: formInsumo.es_alergeno
    }

    try {
      await crearInsumo(datosInsumo)
      setMensajeInsumo(`Insumo / Materia prima "${datosInsumo.nombre}" registrado exitosamente en almacén.`)
      setFormInsumo(FORM_INSUMO_INICIAL)
    } catch (err) {
      setErrorInsumo(err.message)
    } finally {
      setCargando(false)
    }
  }

  return (
    <div>
      <div style={estilos.header}>
        ⚙️ SmartCoffee Nexus — Panel de Administración
      </div>

      {/* TA10-2 Componente Activo: Intercepta notificaciones globales flotantes de stock crítico */}
      <ToastNotification />

      {/* Tabs de Navegación del Panel de Control */}
      <div style={estilos.pestanasContenedor}>
        <button 
          style={tabActiva === 'productos' ? estilos.pestanaBtnActiva : estilos.pestanaBtn}
          onClick={() => setTabActiva('productos')}
        >
          📦 Gestión de Catálogo
        </button>
        <button 
          style={tabActiva === 'inventario' ? estilos.pestanaBtnActiva : estilos.pestanaBtn}
          onClick={() => setTabActiva('inventario')}
        >
          🌾 Almacén e Insumos
        </button>
      </div>

      <div style={estilos.contenedor}>

        {/* ── SECCIÓN 1: CONTROL DE CATÁLOGO (PRODUCTOS) ── */}
        {tabActiva === 'productos' && (
          <>
            <div style={estilos.seccion}>
              <div style={estilos.titulo}>
                {editandoId ? `✏️ Editar producto #${editandoId}` : '➕ Nuevo producto'}
              </div>

              {mensaje && <div style={estilos.mensajeExito}>✅ {mensaje}</div>}
              {error && <div style={estilos.mensajeError}>⚠️ {error}</div>}

              <form onSubmit={manejarEnvio} style={estilos.formulario}>
                <div>
                  <label style={estilos.label}>Nombre *</label>
                  <input
                    style={estilos.input}
                    name="nombre"
                    value={form.nombre}
                    onChange={manejarCambio}
                    placeholder="Ej: Café Latte"
                    maxLength={150}
                  />
                </div>

                <div>
                  <label style={estilos.label}>Precio (S/) *</label>
                  <input
                    style={estilos.input}
                    name="precio"
                    type="number"
                    step="0.10"
                    min="0.10"
                    value={form.precio}
                    onChange={manejarCambio}
                    placeholder="Ej: 8.50"
                  />
                </div>

                <div>
                  <label style={estilos.label}>Categoría *</label>
                  <select
                    style={estilos.select}
                    name="id_categoria"
                    value={form.id_categoria}
                    onChange={manejarCambio}
                  >
                    <option value="">Selecciona una categoría</option>
                    {categorias.map(cat => (
                      <option key={cat.id_categoria} value={cat.id_categoria}>
                        {cat.nombre}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label style={estilos.label}>URL de imagen</label>
                  <input
                    style={estilos.input}
                    name="imagen_url"
                    value={form.imagen_url}
                    onChange={manejarCambio}
                    placeholder="https://..."
                    maxLength={300}
                  />
                </div>

                <div style={estilos.campoCompleto}>
                  <label style={estilos.label}>Descripción</label>
                  <textarea
                    style={estilos.textarea}
                    name="descripcion"
                    value={form.descripcion}
                    onChange={manejarCambio}
                    placeholder="Descripción del producto..."
                  />
                </div>

                <div style={estilos.campoCompleto}>
                  <label style={estilos.checkboxFila}>
                    <input
                      type="checkbox"
                      name="disponible"
                      checked={form.disponible}
                      onChange={manejarCambio}
                    />
                    Producto disponible en carta
                  </label>
                </div>

                <div style={estilos.botones}>
                  <button type="submit" style={estilos.btnGuardar} disabled={cargando}>
                    {cargando ? 'Guardando...' : editandoId ? 'Actualizar producto' : 'Crear producto'}
                  </button>
                  {editandoId && (
                    <button type="button" style={estilos.btnCancelar} onClick={cancelarEdicion}>
                      Cancelar
                    </button>
                  )}
                </div>
              </form>
            </div>

            <div style={estilos.seccion}>
              <div style={estilos.titulo}>📋 Productos registrados ({productos.length})</div>
              <table style={estilos.tablaProductos}>
                <thead>
                  <tr>
                    <th style={estilos.th}>ID</th>
                    <th style={estilos.th}>Nombre</th>
                    <th style={estilos.th}>Precio</th>
                    <th style={estilos.th}>Categoría</th>
                    <th style={estilos.th}>Estado</th>
                    <th style={estilos.th}>Acción</th>
                  </tr>
                </thead>
                <tbody>
                  {productos.map(p => (
                    <tr key={p.id_producto}>
                      <td style={estilos.td}>{p.id_producto}</td>
                      <td style={estilos.td}>{p.nombre}</td>
                      <td style={estilos.td}>S/ {p.precio.toFixed(2)}</td>
                      <td style={estilos.td}>
                        {categorias.find(c => c.id_categoria === p.id_categoria)?.nombre || '—'}
                      </td>
                      <td style={estilos.td}>
                        <span style={p.disponible ? estilos.badgeDisponible : estilos.badgeNoDisponible}>
                          {p.disponible ? 'Disponible' : 'No disponible'}
                        </span>
                      </td>
                      <td style={estilos.td}>
                        <button style={estilos.btnEditar} onClick={() => iniciarEdicion(p)}>
                          Editar
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}

        {/* ── NUEVA SECCIÓN 2: INTERFAZ ADMINISTRATIVA DE INSUMOS (TA09-3) ── */}
        {tabActiva === 'inventario' && (
          <div style={estilos.seccion}>
            <div style={estilos.titulo}>🌾 Registrar Materia Prima / Insumo</div>

            {mensajeInsumo && <div style={estilos.mensajeExito}>✅ {mensajeInsumo}</div>}
            {errorInsumo && <div style={estilos.mensajeError}>⚠️ {errorInsumo}</div>}

            <form onSubmit={manejarEnvioInsumo} style={estilos.formulario}>
              <div>
                <label style={estilos.label}>Nombre del Insumo *</label>
                <input
                  style={estilos.input}
                  name="nombre"
                  value={formInsumo.nombre}
                  onChange={manejarCambioInsumo}
                  placeholder="Ej: Café en grano Blend"
                />
              </div>

              <div>
                <label style={estilos.label}>Unidad de Medida</label>
                <select
                  style={estilos.select}
                  name="text"
                  name="unidad_medida"
                  value={formInsumo.unidad_medida}
                  onChange={manejarCambioInsumo}
                >
                  <option value="gr">Gramos (gr)</option>
                  <option value="ml">Mililitros (ml)</option>
                  <option value="unidades">Unidades (und)</option>
                </select>
              </div>

              <div>
                <label style={estilos.label}>Stock Inicial Actual *</label>
                <input
                  style={estilos.input}
                  name="stock_actual"
                  type="number"
                  min="0"
                  step="any"
                  value={formInsumo.stock_actual}
                  onChange={manejarCambioInsumo}
                  placeholder="Ej: 5000"
                />
              </div>

              <div>
                <label style={estilos.label}>Nivel de Stock Mínimo (Alerta) *</label>
                <input
                  style={estilos.input}
                  name="stock_minimo"
                  type="number"
                  min="0"
                  step="any"
                  value={formInsumo.stock_minimo}
                  onChange={manejarCambioInsumo}
                  placeholder="Ej: 500"
                />
              </div>

              <div style={estilos.campoCompleto}>
                <label style={estilos.checkboxFila}>
                  <input
                    type="checkbox"
                    name="es_alergeno"
                    checked={formInsumo.es_alergeno}
                    onChange={manejarCambioInsumo}
                  />
                  Este insumo está catalogado como un <strong>Alérgeno Crítico</strong>
                </label>
              </div>

              <div style={estilos.botones}>
                <button type="submit" style={estilos.btnGuardar} disabled={cargando}>
                  {cargando ? 'Registrando...' : 'Registrar Insumo'}
                </button>
              </div>
            </form>
          </div>
        )}

      </div>
    </div>
  )
}