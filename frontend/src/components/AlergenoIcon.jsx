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