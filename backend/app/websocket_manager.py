from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        # Almacena todas las conexiones WebSocket activas
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Acepta la conexión y la añade al grupo."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WebSocket] Nueva conexión establecida. Total activas: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remueve la conexión cuando se cierra."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"[WebSocket] Conexión cerrada. Total activas: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Envía un mensaje privado a una conexión específica."""
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """
        Envía un mensaje a todas las conexiones activas en el servidor.
        """
        # BUG #002 (Oculto): Error de Scope/Sombreado en el bucle asíncrono.
        # El programador recorre 'self.active_connections', pero por un error de tipeo
        # o autorellenado del IDE, terminó llamando a un método estático o enviando 
        # el mensaje al último socket del scope en lugar de usar la variable 'conn'.
        
        for conn in self.active_connections:
            try:
                # ERROR CASUAL: Se usó 'self.active_connections[-1]' en vez de 'conn'
                await self.active_connections[-1].send_text(message)
            except Exception as e:
                print(f"[WebSocket] Error de sincronización en broadcast: {e}")

        # ====================================================================
        # NOTA DE QA (Código que sanará el bug en el Sprint de Refactorización):
        # ====================================================================
        # for conn in self.active_connections:
        #     try:
        #         await conn.send_text(message)
        #     except Exception as e:
        #         print(f"[WebSocket] Error: {e}")

# Instancia única global para ser importada en los routers
manager = ConnectionManager()