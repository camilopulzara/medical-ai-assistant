"""
Servicio de IA Conversacional con LangGraph + Google Gemini
Agente con nodos de decisión para procesamiento rápido de solicitudes médicas
"""

import os
import time
import logging
import re
import requests
import json
from typing import Optional, Tuple, Dict
from enum import Enum
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from jose import jwt

# LangGraph imports
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

# Database imports
from database import SessionLocal
from models import Patient, Appointment, Document
from config import settings
from sqlalchemy.orm import Session

# Load environment variables
load_dotenv()

# Logging
logger = logging.getLogger(__name__)


# ============================================================================
# STATE MANAGEMENT
# ============================================================================

class MedicalAIState(TypedDict):
    """Estado pasado entre los nodos del grafo"""
    user_message: str
    patient_id: int
    intent: str  # appointment, document, medical_history, general
    db_context: Optional[str]
    chat_history: Optional[str]
    ai_response: str
    start_time: float


# ============================================================================
# INTENT TYPES
# ============================================================================

class IntentType(Enum):
    APPOINTMENT = "appointment"
    DOCUMENT = "document"
    MEDICAL_HISTORY = "medical_history"
    RESCHEDULE = "reschedule"
    CONFIRM_RESCHEDULE = "confirm_reschedule"
    CANCEL_RESCHEDULE = "cancel_reschedule"
    GENERAL = "general"


# ============================================================================
# MEDICAL AI AGENT WITH LANGGRAPH (OPTIMIZED)
# ============================================================================

class MedicalAIAgent:
    """Agente de IA médico usando LangGraph con Google Gemini"""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        
        # Initialize Groq client
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"
        self.pending_reschedules: Dict[int, date] = {}
        
        # Build the LangGraph
        self.graph = self._build_graph()
        self.compiled_graph = self.graph.compile()
    
    # ========================================================================
    # HELPER: EXTRACT DATE FROM MESSAGE
    # ========================================================================
    
    def _extract_date_from_message(self, message: str) -> Optional[date]:
        """
        Intenta extraer una fecha del mensaje.
        Soporta: "10 de marzo", "marzo 10", "10/03", "2026-03-10"
        """
        message_lower = message.lower()
        
        # Mapeo de meses en español
        months_es = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }
        
        # Patrón: "10 de marzo" o "10 de marzo de 2026"
        pattern1 = r'(\d{1,2})\s+de\s+(\w+)(?:\s+de\s+(\d{4}))?'
        match = re.search(pattern1, message_lower)
        if match:
            day = int(match.group(1))
            month_name = match.group(2).lower()
            year = int(match.group(3)) if match.group(3) else datetime.now().year
            
            if month_name in months_es:
                month = months_es[month_name]
                try:
                    return datetime(year, month, day).date()
                except ValueError:
                    return None
        
        # Patrón: "10/03" o "10/03/2026"
        pattern2 = r'(\d{1,2})/(\d{1,2})(?:/(\d{4}))?'
        match = re.search(pattern2, message_lower)
        if match:
            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3)) if match.group(3) else datetime.now().year
            try:
                return datetime(year, month, day).date()
            except ValueError:
                return None
        
        return None

    def _is_confirmation_message(self, message: str) -> bool:
        message = message.strip().lower()
        confirmation_keywords = ["si", "sí", "confirmo", "confirmar", "ok", "dale", "acepto", "de acuerdo"]
        return any(word in message for word in confirmation_keywords)

    def _is_cancel_message(self, message: str) -> bool:
        message = message.strip().lower()
        cancel_keywords = ["cancelar", "cancela", "no", "mejor no", "olvidalo", "olvídalo"]
        return any(word in message for word in cancel_keywords)

    def _is_provider_query(self, message: str) -> bool:
        message = message.strip().lower()
        provider_keywords = [
            "doctor", "doctores", "médico", "medico", "especialidad", "especialidades",
            "horario", "horarios", "turno", "profesional", "profesionales"
        ]
        return any(word in message for word in provider_keywords)

    def _format_date_es(self, dt: date) -> str:
        months = {
            1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
            7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
        }
        return f"{dt.day} de {months[dt.month]} de {dt.year}"
    
    def _try_reschedule_appointment(self, patient_id: int, new_date: date) -> Tuple[bool, str]:
        """
        Intenta reprogramar la próxima cita del paciente.
        Retorna: (éxito, mensaje)
        """
        try:
            # Obtener la próxima cita (sin reprogramar) del paciente
            # Convertir a date para comparación consistente
            today = datetime.now().date()
            
            appointment = self.db.query(Appointment).filter(
                Appointment.patient_id == patient_id
            ).all()
            
            # Filtrar qué citas son futuras (comparando dates)
            future_appointments = []
            for appt in appointment:
                appt_date = appt.appointment_date
                if isinstance(appt_date, datetime):
                    appt_date = appt_date.date()
                if appt_date >= today:
                    future_appointments.append(appt)
            
            if not future_appointments:
                return False, "No se encontró una cita pendiente para reprogramar."
            
            # Tomar la más próxima
            appointment = sorted(future_appointments, key=lambda a: a.appointment_date)[0]
            
            old_date = appointment.appointment_date.strftime('%Y-%m-%d') if hasattr(appointment.appointment_date, 'strftime') else str(appointment.appointment_date)
            
            # Actualizar la cita - convertir date a datetime si es necesario
            if isinstance(new_date, datetime):
                appointment.appointment_date = new_date
            else:
                appointment.appointment_date = datetime.combine(new_date, datetime.min.time())
            
            self.db.commit()
            
            new_date_str = new_date.strftime('%Y-%m-%d') if hasattr(new_date, 'strftime') else str(new_date)
            return True, f"Cita reprogramada exitosamente de {old_date} a {new_date_str}."
        
        except Exception as e:
            logger.error(f"Error rescheduling appointment: {e}")
            self.db.rollback()
            return False, "Error al reprogramar la cita. Intenta de nuevo."

    def _fallback_response(self, intent: str, db_context: str) -> str:
        """Respuesta de contingencia cuando el proveedor de IA falla."""
        if intent == IntentType.APPOINTMENT.value:
            return f"No pude consultar la IA en este momento, pero aquí tienes tus datos de citas:\n{db_context}"
        if intent == IntentType.DOCUMENT.value:
            return f"No pude consultar la IA en este momento, pero aquí tienes tus documentos:\n{db_context}"
        if intent == IntentType.MEDICAL_HISTORY.value:
            return f"No pude consultar la IA en este momento, pero este es tu resumen:\n{db_context}"
        return "El servicio de IA está inestable en este momento. Intenta de nuevo en unos segundos."
    
    def _generate_document_download_links(self, patient_id: int, documents: list) -> str:
        """Genera enlaces de descarga seguros para documentos médicos."""
        if not documents:
            return "No tienes documentos disponibles."
        
        doc_lines = []
        for doc in documents:
            # Crear payload para JWT
            payload = {
                "document_id": doc.id,
                "patient_id": patient_id,
                "exp": datetime.utcnow() + timedelta(minutes=settings.DOWNLOAD_TOKEN_EXPIRE_MINUTES),
                "type": "download"
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
            download_url = f"/api/documents/download/{doc.id}?token={token}"
            
            file_type = f" ({doc.file_type})" if doc.file_type else ""
            doc_lines.append(f"• {doc.title}{file_type}\n  Descargar: {download_url}")
        
        return "Documentos disponibles:\n" + "\n".join(doc_lines)
    
    def _build_graph(self) -> StateGraph:
        """Construye el grafo con nodos optimizados"""
        graph = StateGraph(MedicalAIState)
        
        # Nodos del grafo - flujo simplificado
        graph.add_node("detect_and_query", self._detect_intent_and_query_node)
        graph.add_node("generate_response", self._generate_response_node)
        
        # Aristas - flujo directo sin validador separado
        graph.add_edge(START, "detect_and_query")
        graph.add_edge("detect_and_query", "generate_response")
        graph.add_edge("generate_response", END)
        
        return graph
    
    # ========================================================================
    # NODO 1: DETECT INTENT + QUERY DB (COMBINADO)
    # ========================================================================
    
    def _detect_intent_and_query_node(self, state: MedicalAIState) -> MedicalAIState:
        """
        Nodo 1: Detecta intención Y consulta BD en un paso
        Soporta: citas, documentos, historial, reprogramación
        """
        start = time.time()
        message = state["user_message"].lower()
        
        # Detectar intención rápidamente
        appointment_keywords = ["cita", "appointment", "agendar", "reservar", "horario", "fecha", "próxima"]
        document_keywords = ["documento", "archivo", "reporte", "resultado", "prueba", "examen"]
        history_keywords = ["historial", "historia", "antecedentes", "diagnóstico", "enfermedad"]
        reschedule_keywords = ["reprogramar", "cambiar cita", "mover cita", "otra fecha", "nueva fecha", "diferente fecha", "postponer", "nueva cita"]
        
        # Si hay una reprogramación pendiente, priorizar confirmación/cancelación
        if state["patient_id"] in self.pending_reschedules and self._is_confirmation_message(message):
            intent = IntentType.CONFIRM_RESCHEDULE.value
        elif state["patient_id"] in self.pending_reschedules and self._is_cancel_message(message):
            intent = IntentType.CANCEL_RESCHEDULE.value
        elif any(keyword in message for keyword in reschedule_keywords):
            intent = IntentType.RESCHEDULE.value
        elif any(keyword in message for keyword in appointment_keywords):
            intent = IntentType.APPOINTMENT.value
        elif any(keyword in message for keyword in document_keywords):
            intent = IntentType.DOCUMENT.value
        elif any(keyword in message for keyword in history_keywords):
            intent = IntentType.MEDICAL_HISTORY.value
        else:
            intent = IntentType.GENERAL.value
        
        state["intent"] = intent
        
        # QUERY BD UNA SOLA VEZ
        db_context = ""
        try:
            patient = self.db.query(Patient).filter(Patient.id == state["patient_id"]).first()
            
            if not patient:
                db_context = "No se encontró información del paciente."
            else:
                # Obtener datos relevantes según la intención
                if intent == IntentType.CONFIRM_RESCHEDULE.value:
                    requested_date = self.pending_reschedules.get(state["patient_id"])
                    if requested_date:
                        db_context = f"Confirmación recibida para reprogramar al {requested_date.strftime('%Y-%m-%d')}."
                    else:
                        db_context = "No hay una reprogramación pendiente para confirmar."

                elif intent == IntentType.CANCEL_RESCHEDULE.value:
                    db_context = "El usuario canceló la reprogramación pendiente."

                elif intent == IntentType.RESCHEDULE.value:
                    # Para reprogramar, obtener la próxima cita
                    appointments = self.db.query(Appointment).filter(
                        Appointment.patient_id == state["patient_id"],
                        Appointment.appointment_date >= datetime.now()
                    ).order_by(Appointment.appointment_date).all()
                    
                    if appointments:
                        next_appt = appointments[0]
                        appt_date = next_appt.appointment_date.strftime('%Y-%m-%d') if hasattr(next_appt.appointment_date, 'strftime') else str(next_appt.appointment_date)
                        db_context = f"Próxima cita: {appt_date} ({next_appt.reason})"
                    else:
                        db_context = f"{patient.name} no tiene citas pendientes."
                
                elif intent == IntentType.APPOINTMENT.value:
                    appointments = self.db.query(Appointment).filter(
                        Appointment.patient_id == state["patient_id"]
                    ).all()
                    
                    if appointments:
                        appt_list = [
                            f"{a.appointment_date.strftime('%Y-%m-%d') if hasattr(a.appointment_date, 'strftime') else str(a.appointment_date)}: {a.reason}"
                            for a in appointments
                        ]
                        db_context = f"Citas de {patient.name}:\n" + "\n".join(appt_list)
                    else:
                        db_context = f"{patient.name} no tiene citas programadas."
                
                elif intent == IntentType.DOCUMENT.value:
                    documents = self.db.query(Document).filter(
                        Document.patient_id == state["patient_id"]
                    ).order_by(Document.uploaded_at.desc()).all()
                    
                    if documents:
                        db_context = self._generate_document_download_links(state["patient_id"], documents)
                    else:
                        db_context = f"{patient.name} no tiene documentos."
                
                elif intent == IntentType.MEDICAL_HISTORY.value:
                    db_context = f"Paciente: {patient.name}, Teléfono: {patient.phone}"
                
                else:  # GENERAL
                    db_context = (
                        f"Paciente: {patient.name}. "
                        "No hay información de doctores, especialidades ni horarios en el contexto actual."
                    )
        
        except Exception as e:
            db_context = "Error recuperando datos"
            logger.error(f"DB Error: {e}")
        
        state["db_context"] = db_context
        elapsed = time.time() - start
        logger.info(f"Node 1 (Intent+DB): {elapsed:.2f}s | Intent: {intent}")
        
        return state
    
    # ========================================================================
    # NODO 2: GENERATE RESPONSE (OPTIMIZADO)
    # ========================================================================
    
    def _generate_response_node(self, state: MedicalAIState) -> MedicalAIState:
        """
        Nodo 2: Genera respuesta con Google Gemini API
        Maneja reprogramación de citas si es necesario
        """
        start = time.time()
        
        intent = state["intent"]
        db_context = state["db_context"]
        chat_history = state.get("chat_history", "")
        user_message = state["user_message"]
        reschedule_status = ""
        
        # Reprogramación con doble confirmación
        if intent == IntentType.RESCHEDULE.value:
            new_date = self._extract_date_from_message(user_message)
            logger.info(f"RESCHEDULE detected. Extracted date: {new_date}")

            if new_date:
                self.pending_reschedules[state["patient_id"]] = new_date
                ai_response = (
                    f"Puedo reprogramar tu cita para el {self._format_date_es(new_date)}. "
                    "Responde 'sí' para confirmar o 'cancelar' para anular."
                )
                state["ai_response"] = ai_response
                elapsed = time.time() - start
                logger.info(f"Node 2 (Reschedule pending): {elapsed:.2f}s")
                return state
            else:
                logger.warning(f"No date extracted from message: {user_message}")
                ai_response = "No pude detectar la nueva fecha. Ejemplo: 'reprogramar para 15 de marzo'."
                state["ai_response"] = ai_response
                elapsed = time.time() - start
                logger.info(f"Node 2 (Reschedule missing date): {elapsed:.2f}s")
                return state

        if intent == IntentType.CONFIRM_RESCHEDULE.value:
            requested_date = self.pending_reschedules.get(state["patient_id"])
            if not requested_date:
                state["ai_response"] = "No tengo una reprogramación pendiente para confirmar."
                elapsed = time.time() - start
                logger.info(f"Node 2 (No pending reschedule): {elapsed:.2f}s")
                return state

            success, status_msg = self._try_reschedule_appointment(state["patient_id"], requested_date)
            logger.info(f"Reschedule confirm result - Success: {success}, Message: {status_msg}")
            del self.pending_reschedules[state["patient_id"]]

            if success:
                state["ai_response"] = f"Listo, tu cita fue reprogramada para el {self._format_date_es(requested_date)}."
            else:
                state["ai_response"] = status_msg

            elapsed = time.time() - start
            logger.info(f"Node 2 (Reschedule confirmed): {elapsed:.2f}s")
            return state

        if intent == IntentType.CANCEL_RESCHEDULE.value:
            if state["patient_id"] in self.pending_reschedules:
                del self.pending_reschedules[state["patient_id"]]
            state["ai_response"] = "Perfecto, cancelé la reprogramación pendiente."
            elapsed = time.time() - start
            logger.info(f"Node 2 (Reschedule canceled): {elapsed:.2f}s")
            return state

        if intent == IntentType.GENERAL.value and self._is_provider_query(user_message):
            state["ai_response"] = (
                "No tengo datos de doctores, especialidades ni horarios en este momento. "
                "Si quieres, puedo ayudarte con tu cita, documentos o historial disponible."
            )
            elapsed = time.time() - start
            logger.info(f"Node 2 (Provider guardrail): {elapsed:.2f}s")
            return state
        
        # PROMPT SIMPLE
        simple_prompt = f"""Eres un asistente médico.

Reglas estrictas:
- Usa únicamente la información del Contexto.
- No inventes nombres de doctores, especialidades, horarios ni datos clínicos.
- Si el dato no está en el Contexto, responde explícitamente: "No tengo esa información en este momento".
- IMPORTANTE: Cuando el Contexto incluye enlaces de descarga (Descargar:), SIEMPRE incluye el enlace COMPLETO en tu respuesta.
- Responde en español y de forma breve.

Historial reciente de conversación:
{chat_history if chat_history else 'Sin historial previo relevante.'}

Contexto: {db_context}

Pregunta: {user_message}

Respuesta (máximo 3 oraciones, incluye enlaces completos si están disponibles):"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Eres un asistente médico profesional. Responde siempre en español de manera clara y concisa."
                    },
                    {
                        "role": "user",
                        "content": simple_prompt
                    }
                ],
                "temperature": 0.5,
                "max_tokens": 200
            }
            
            # Retry logic para mayor confiabilidad
            max_retries = 2
            for attempt in range(max_retries + 1):
                try:
                    response = requests.post(self.groq_url, headers=headers, json=data, timeout=30)
                    response.raise_for_status()
                    ai_response = response.json()["choices"][0]["message"]["content"]
                    
                    # Validación mínima
                    if not ai_response or len(ai_response.strip()) == 0:
                        ai_response = "No pude procesar tu solicitud."
                    elif len(ai_response) > 500:
                        ai_response = ai_response[:500] + "..."
                    break
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries:
                        logger.warning(f"Groq attempt {attempt + 1} failed, retrying... Error: {e}")
                        time.sleep(1)
                    else:
                        raise
            
        except Exception as e:
            import traceback
            logger.error(f"Groq Error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            status_code = getattr(getattr(e, "response", None), "status_code", None)
            if status_code == 429:
                ai_response = "El servicio de IA está saturado. Intenta nuevamente en unos segundos."
            elif status_code in (401, 403):
                ai_response = "La configuración de IA no es válida. Revisa la API key de Groq."
            else:
                ai_response = self._fallback_response(intent, db_context)
        
        state["ai_response"] = ai_response
        elapsed = time.time() - start
        logger.info(f"Node 2 (Gemini): {elapsed:.2f}s")
        
        return state
    
    # ========================================================================
    # INTERFAZ PÚBLICA
    # ========================================================================
    
    def process_message(self, message: str, patient_id: int, chat_history: str = "") -> str:
        """
        Punto de entrada - ejecuta el flujo optimizado
        """
        initial_state: MedicalAIState = {
            "user_message": message,
            "patient_id": patient_id,
            "intent": "",
            "db_context": "",
            "chat_history": chat_history,
            "ai_response": "",
            "start_time": time.time()
        }
        
        try:
            final_state = self.compiled_graph.invoke(initial_state)
            total_time = time.time() - initial_state["start_time"]
            logger.info(f"Total time: {total_time:.2f}s")
            return final_state["ai_response"]
        
        except Exception as e:
            import traceback
            logger.error(f"Process Error: {e}")
            logger.error(f"Process Traceback: {traceback.format_exc()}")
            return "Error procesando mensaje. Intenta de nuevo."


# Instancia global del agente
medical_agent = MedicalAIAgent()
