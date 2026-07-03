/**
 * TA02-3: Componente visual que muestra una etiqueta de advertencia de alérgeno.
 * Se renderiza únicamente cuando es_alergeno es true.
 *
 * BUG #003 visible aquí: como el endpoint GET /productos devuelve
 * es_alergeno: false siempre, este ícono nunca aparece en el catálogo
 * aunque el producto sí contenga insumos alérgenos.
 * Solo aparece correctamente en el detalle individual (GET /productos/{id})
 * porque ese endpoint sí hace el JOIN correcto.
 */

const estilos = {
  badge: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '4px',
    backgroundColor: '#FFF3CD',
    border: '1px solid #FFCA2C',
    color: '#856404',
    borderRadius: '12px',
    padding: '2px 8px',
    fontSize: '11px',
    fontWeight: '600',
    marginTop: '4px'
  },
  icono: {
    fontSize: '13px'
  }
}

export default function AlergenoIcon({ visible = false }) {
  // TA02-4: Solo renderiza si el producto tiene alérgenos confirmados
  if (!visible) return null

  return (
    <span style={estilos.badge}>
      <span style={estilos.icono}>⚠️</span>
      Contiene alérgenos
    </span>
  )
}