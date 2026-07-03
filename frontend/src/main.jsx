import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

// Aplicamos unos estilos mínimos globales directo en el render inicial para unificar fuentes y márgenes
const inicializarEstilosGlobales = () => {
  const estilo = document.createElement('style')
  estilo.innerHTML = `
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    body {
      background-color: #F5F0EA;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }
  `
  document.head.appendChild(estilo)
}

inicializarEstilosGlobales()

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)