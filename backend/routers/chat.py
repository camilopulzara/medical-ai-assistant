from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict, List
from database import get_db
from models import ChatSession, ChatMessage, Patient
import json
import uuid
from datetime import datetime

router = APIRouter()


class ConnectionManager:
    """Gestor de conexiones WebSocket"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_message(self, message: str, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/chat/{patient_email}")
async def websocket_chat(websocket: WebSocket, patient_email: str):
    """WebSocket endpoint para chat en tiempo real"""
    
    # Generar session_id único
    session_id = str(uuid.uuid4())
    
    await manager.connect(websocket, session_id)
    
    # TODO: Aquí conectarás con la base de datos
    # Por ahora es un echo simple
    
    try:
        # Mensaje de bienvenida
        await manager.send_message(
            json.dumps({
                "role": "assistant",
                "content": f"¡Hola! Soy tu asistente médico. ¿En qué puedo ayudarte hoy?",
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id
            }),
            session_id
        )
        
        while True:
            # Recibir mensaje del usuario
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Guardar mensaje del usuario (TODO: guardar en DB)
            user_message = message_data.get("content", "")
            
            # TODO: Aquí irá la lógica de LangGraph
            # Por ahora solo hacemos echo
            response = f"Recibí tu mensaje: {user_message}. (Próximamente con IA)"
            
            # Enviar respuesta
            await manager.send_message(
                json.dumps({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat(),
                    "session_id": session_id
                }),
                session_id
            )
            
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        print(f"Cliente desconectado: {session_id}")
    except Exception as e:
        print(f"Error en WebSocket: {e}")
        manager.disconnect(session_id)
