import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import ClienteView from './pages/ClienteView'
import AdminView from './pages/AdminView'
import CocinaView from './pages/CocinaView'


const estilos = {
  pantallaInicio: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    background: '#F5F0EA',
    fontFamily: 'system-ui, sans-serif',
    padding: '16px',
    textAlign: 'center'
  },
  card: {
    background: '#ffffff',
    padding: '32px',
    borderRadius: '16px',
    boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
    maxWidth: '400px',
    width: '100%'
  },
  titulo: {
    color: '#6B4C2A',
    fontWeight: '700',
    fontSize: '24px',
    marginBottom: '8px'
  },
  texto: {
    color: '#595959',
    fontSize: '14px',
    lineHeight: '1.5',
    marginBottom: '24px'
  },
  enlaceAdmin: {
    display: 'inline-block',
    color: '#6B4C2A',
    textDecoration: 'none',
    fontWeight: '600',
    fontSize: '14px',
    borderBottom: '1px dashed #6B4C2A'
  }
}

// Vista interna temporal en caso entren a la raíz sin QR
function InicioSinQR() {
  return (
    <div style={estilos.pantallaInicio}>
      <div style={estilos.card}>
        <span style={{ fontSize: '48px' }}>☕</span>
        <h1 style={estilos.titulo}>SmartCoffee Nexus</h1>
        <p style={estilos.texto}>
          Por favor, escanea el código QR de tu mesa para poder ver la carta interactiva y realizar tu pedido de forma automática.
        </p>
        <Link to="/admin" style={estilos.enlaceAdmin}>
          ⚙️ Ir al Panel de Administración
        </Link>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Ruta base informativa */}
        <Route path="/" element={<InicioSinQR />} />

        {/* HU14 / TA14-1: Ruta dinámica que captura el QR code de la mesa */}
        <Route path="/mesa/:qrCode" element={<ClienteView />} />

        {/* TA01-2 / TA01-3: Ruta de administración del catálogo */}
        <Route path="/admin" element={<AdminView />} />

        {/* Fallback para cualquier ruta no definida */}
        <Route path="*" element={<InicioSinQR />} />

        <Route path="/cocina" element={<CocinaView />} />
      </Routes>
    </BrowserRouter>
  )
}