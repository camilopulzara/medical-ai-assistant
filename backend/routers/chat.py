from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database import get_db
from models import ChatSession, ChatMessage, Patient
from services.ai_agent import medical_agent
import uuid
from datetime import datetime
import json

router = APIRouter(prefix="/api/chat", tags=["chat"])


class MessageRequest(BaseModel):
    message: str
    session_id: str = None
    patient_id: int = 12  # ID del primer paciente disponible


class CreateSessionRequest(BaseModel):
    patient_id: int = 12  # Modelo específico para crear sesión


class MessageResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str


class SessionResponse(BaseModel):
    session_id: str
    patient_id: int


def sanitize_text(text: str) -> str:
    """Sanitiza texto para evitar problemas de encoding"""
    try:
        # Convertir a bytes UTF-8 y de vuelta para limpiar
        return text.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
    except:
        return "Error procesando mensaje"


def build_recent_history(db: Session, chat_session_id: int, limit: int = 8) -> str:
    """Construye historial corto para mantener continuidad conversacional."""
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == chat_session_id)
        .order_by(ChatMessage.timestamp.desc())
        .limit(limit)
        .all()
    )

    if not messages:
        return ""

    # Vienen en orden descendente; invertir para mantener secuencia natural
    messages = list(reversed(messages))
    lines = []
    for msg in messages:
        role = "Usuario" if msg.role == "user" else "Asistente"
        content = sanitize_text(msg.content) if msg.content else ""
        lines.append(f"{role}: {content}")

    return "\n".join(lines)


@router.post("/send", response_model=MessageResponse)
def send_message(request: MessageRequest, db: Session = Depends(get_db)):
    """
    Envía un mensaje y obtiene respuesta del asistente de IA
    """
    try:
        # Sanitizar entrada
        clean_message = sanitize_text(request.message)
        
        # Crear o usar sesión existente
        session_id = request.session_id or str(uuid.uuid4())
        
        # Obtener o crear sesión de chat
        chat_session = db.query(ChatSession).filter(
            ChatSession.session_id == session_id
        ).first()
        
        if not chat_session:
            chat_session = ChatSession(
                patient_id=request.patient_id,
                session_id=session_id,
                is_active=True
            )
            db.add(chat_session)
            db.commit()
        
        # Guardar mensaje del usuario
        user_message = ChatMessage(
            session_id=chat_session.id,
            role="user",
            content=clean_message,
            timestamp=datetime.utcnow()
        )
        db.add(user_message)
        db.commit()
        
        # Construir historial reciente para contexto conversacional
        recent_history = build_recent_history(db, chat_session.id, limit=8)

        # Procesar con IA y obtener respuesta
        try:
            response_text = medical_agent.process_message(
                clean_message,
                request.patient_id,
                recent_history
            )
            # Sanitizar respuesta de IA
            response_text = sanitize_text(response_text)
        except Exception as ai_error:
            print(f"Error en IA: {ai_error}")
            response_text = "Hubo un error al procesar tu solicitud. Intenta nuevamente."
        
        # Guardar respuesta de IA
        ai_message = ChatMessage(
            session_id=chat_session.id,
            role="assistant",
            content=response_text,
            timestamp=datetime.utcnow()
        )
        db.add(ai_message)
        db.commit()
        
        return MessageResponse(
            response=response_text,
            session_id=session_id,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        print(f"Error en chat: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error procesando mensaje")


@router.post("/sessions", response_model=SessionResponse)
def create_session(request: CreateSessionRequest, db: Session = Depends(get_db)):
    """Crea una nueva sesión de chat"""
    try:
        session_id = str(uuid.uuid4())
        
        chat_session = ChatSession(
            patient_id=request.patient_id,
            session_id=session_id,
            is_active=True
        )
        db.add(chat_session)
        db.commit()
        
        return SessionResponse(
            session_id=session_id,
            patient_id=request.patient_id
        )
        
    except Exception as e:
        print(f"Error al crear sesion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}")
def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """Obtiene el historial de chat de una sesión"""
    try:
        chat_session = db.query(ChatSession).filter(
            ChatSession.session_id == session_id
        ).first()
        
        if not chat_session:
            raise HTTPException(status_code=404, detail="Sesion no encontrada")
        
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == chat_session.id
        ).all()
        
        return {
            "session_id": session_id,
            "patient_id": chat_session.patient_id,
            "messages": [
                {
                    "role": msg.role,
                    "content": sanitize_text(msg.content) if msg.content else "",
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
                }
                for msg in messages
            ]
        }
        
    except Exception as e:
        print(f"Error al obtener historial: {e}")
        raise HTTPException(status_code=500, detail=str(e))


