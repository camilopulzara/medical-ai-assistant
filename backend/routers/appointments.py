from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database import get_db
from models import Patient, Appointment
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


# Schemas Pydantic
class AppointmentCreate(BaseModel):
    patient_email: EmailStr
    appointment_date: datetime
    reason: str


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    appointment_date: datetime
    reason: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/", response_model=AppointmentResponse)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    """Crear una nueva cita médica"""
    
    # Buscar o crear paciente
    patient = db.query(Patient).filter(Patient.email == appointment.patient_email).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    # Crear cita
    db_appointment = Appointment(
        patient_id=patient.id,
        appointment_date=appointment.appointment_date,
        reason=appointment.reason,
        status="pending"
    )
    
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    return db_appointment


@router.get("/", response_model=List[AppointmentResponse])
def list_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todas las citas"""
    appointments = db.query(Appointment).offset(skip).limit(limit).all()
    return appointments


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Obtener una cita específica"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    return appointment
