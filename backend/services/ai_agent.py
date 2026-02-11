"""
Servicio de IA con LangGraph
Este archivo contendrá la lógica del agente conversacional
"""

from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
# from langgraph.graph import StateGraph, END

# TODO: Implementar cuando LangGraph esté configurado

class AgentState(TypedDict):
    """Estado del agente conversacional"""
    messages: Sequence[BaseMessage]
    patient_email: str
    intent: str  # appointment, document, general_query
    extracted_info: dict


class MedicalAIAgent:
    """Agente de IA para conversaciones médicas"""
    
    def __init__(self):
        # TODO: Inicializar LangGraph y LLM
        pass
    
    async def process_message(self, message: str, patient_email: str) -> str:
        """
        Procesa un mensaje del usuario y genera respuesta
        
        Args:
            message: Mensaje del usuario
            patient_email: Email del paciente
            
        Returns:
            Respuesta del asistente
        """
        # TODO: Implementar lógica con LangGraph
        # Por ahora retorna respuesta simple
        
        if "cita" in message.lower() or "appointment" in message.lower():
            return "Entiendo que quieres agendar una cita. ¿Para qué fecha te gustaría?"
        
        elif "documento" in message.lower():
            return "Puedo ayudarte con tus documentos médicos. ¿Qué necesitas?"
        
        else:
            return f"Recibí tu mensaje: {message}. Pronto tendré más capacidades con IA."
    
    def detect_intent(self, message: str) -> str:
        """Detecta la intención del usuario"""
        # TODO: Implementar con LLM
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["cita", "appointment", "agendar", "reservar"]):
            return "appointment"
        elif any(word in message_lower for word in ["documento", "document", "resultado", "análisis"]):
            return "document"
        else:
            return "general_query"
    
    def extract_appointment_info(self, messages: list) -> dict:
        """Extrae información de cita de la conversación"""
        # TODO: Implementar con LLM
        return {
            "date": None,
            "time": None,
            "reason": None
        }


# Instancia global del agente
medical_agent = MedicalAIAgent()
