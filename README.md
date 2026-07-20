# ☕ SmartCoffee Nexus

> **Sistema de autoservicio digital para cafeterías basado en códigos QR**
> 
> *Proyecto en desarrollo activo — actualización continua*

---

## 📌 Descripción

SmartCoffee Nexus es un ecosistema digital B2B diseñado para modernizar la operativa de cafeterías. Permite a los clientes escanear un código QR desde su mesa, explorar la carta interactiva y realizar su pedido directamente desde el navegador del celular — sin descargar ninguna aplicación.

El sistema integra tres interfaces sincronizadas en tiempo real:

- **Vista Cliente (PWA)** — acceso por QR, catálogo con alertas de alérgenos, carrito y seguimiento del pedido en tiempo real.
- **Monitor de Cocina** — cola de pedidos ordenada por FIFO, actualización de estados con notificación WebSocket instantánea.
- **Panel Administrativo** — gestión de productos e inventario, alertas de stock crítico y descuento automático de insumos.

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python · FastAPI · SQLAlchemy ORM |
| Base de datos | SQLite (migrable a MySQL/PostgreSQL) |
| Tiempo real | WebSockets nativos de FastAPI |
| Frontend | React 18 · Vite · React Router DOM |
| Testing | pytest · httpx · TestClient |
| Control de versiones | Git · GitHub |

---

## 📁 Estructura del Proyecto

```
smartcoffee_nexus/
├── backend/
│   ├── app/
│   │   ├── main.py                 # Punto de entrada FastAPI
│   │   ├── database.py             # Configuración SQLAlchemy
│   │   ├── models.py               # Modelos ORM (tablas)
│   │   ├── schemas.py              # Validación Pydantic
│   │   ├── seed.py                 # Datos iniciales de prueba
│   │   ├── websocket_manager.py    # Gestor de conexiones WebSocket
│   │   └── routers/
│   │       ├── productos.py        # Catálogo y alérgenos
│   │       ├── pedidos.py          # Pedidos, estados y WebSocket
│   │       ├── mesas.py            # Validación de QR
│   │       └── inventario.py       # Stock, alertas y descuento automático
│   └── tests/
│       ├── conftest.py
│       ├── test_hu01_catalogo.py
│       ├── test_hu02_alergenos.py
│       ├── test_hu05_pedidos.py
│       ├── test_hu06_estados.py
│       ├── test_hu09_inventario.py
│       └── test_hu14_mesas.py
└── frontend/
    └── src/
        ├── App.jsx
        ├── services/api.js
        ├── pages/
        │   ├── ClienteView.jsx
        │   ├── CocinaView.jsx
        │   └── AdminView.jsx
        └── components/
            ├── ProductCard.jsx
            ├── Carrito.jsx
            ├── AlergenoIcon.jsx
            ├── BarraProgreso.jsx
            └── ToastNotification.jsx
```

---

## 🚀 Instalación y Ejecución

### Requisitos previos

- Python 3.11+
- Node.js 18+
- Git

### Backend

```bash
# Clonar el repositorio
git clone https://github.com/Asmoyano/smartcofee_nexus.git
cd smartcofee_nexus/backend

# Crear entorno virtual e instalar dependencias
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

# Poblar la base de datos con datos iniciales
python -m app.seed

# Levantar el servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

La documentación interactiva de la API estará disponible en:
```
http://localhost:8000/docs
```

### Frontend

```bash
cd smartcoffee_nexus/frontend
npm install
npm run dev
```

La aplicación estará disponible en:
```
http://localhost:5173
```

### Acceso por QR (red local)

Para probar el flujo QR desde un dispositivo móvil en la misma red WiFi:

1. Reemplaza `localhost` por la IP local de tu máquina en `frontend/src/services/api.js`
2. Accede desde el celular a:
```
http://[TU_IP]:5173/mesa/QR_MESA_1
```

---

## 🧪 Pruebas

```bash
cd backend

# Ejecutar todos los tests
pytest -v --tb=short

# Ejecutar solo un módulo
pytest tests/test_hu01_catalogo.py -v
```

Los tests utilizan una base de datos SQLite en memoria con `StaticPool` — completamente aislada de la base de datos real.

---

## 📡 Endpoints principales de la API

### Productos
| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/productos` | Lista productos disponibles (con alérgenos) |
| GET | `/productos/{id}` | Detalle de producto con insumos |
| GET | `/productos/categorias` | Lista de categorías |
| POST | `/productos` | Crear nuevo producto |
| PUT | `/productos/{id}` | Actualizar producto |

### Pedidos
| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/pedidos` | Lista pedidos ordenados por FIFO |
| GET | `/pedidos/{id}` | Detalle de un pedido |
| POST | `/pedidos` | Crear nuevo pedido |
| PATCH | `/pedidos/{id}/estado` | Actualizar estado del pedido |
| WS | `/pedidos/ws/{id}` | Canal WebSocket de seguimiento |

### Inventario
| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/inventario` | Lista insumos con stock |
| GET | `/inventario/alertas` | Insumos en nivel crítico |
| PUT | `/inventario/{id}` | Actualizar stock de insumo |
| POST | `/inventario/insumos` | Registrar nuevo insumo |
| POST | `/inventario/descontar-pedido/{id}` | Descuento automático de stock |

### Mesas
| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/mesas/{qr_code}` | Validar código QR de mesa |

---

## 🗃️ Modelo de Datos

El sistema trabaja con las siguientes entidades principales:

```
Categoria → Producto → Receta → Insumo
                ↓
           DetallePedido → Pedido → Mesa
                                  → Cliente
                                  → Feedback
```

---

## 📋 Estado del Proyecto

| Sprint | Historias de Usuario | Estado |
|---|---|---|
| Sprint 1 | HU01 Catálogo · HU02 Alérgenos · HU05 Pedidos · HU14 QR | ✅ Completado |
| Sprint 2 | HU06 Estados cocina · HU07 Tiempo real · HU09 Stock · HU10 Alertas | 🔄 En progreso |
| Sprint 3 | Autenticación · Roles · Modo contingencia | 🔲 Pendiente |
| Sprint 4 | Fidelización · Métricas · Pagos digitales | 🔲 Pendiente |

---

## 👤 Autor

**Adolfo Moyano Tejeda**
Estudiante de Ingeniería de Sistemas — UNAC

[![GitHub](https://img.shields.io/badge/GitHub-Asmoyano-181717?logo=github)](https://github.com/Asmoyano)

---

*Este proyecto se desarrolla como prototipo funcional con fines académicos y de portafolio profesional.*
