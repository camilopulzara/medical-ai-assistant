from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Patient
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/patients", tags=["patients"])


# Schemas Pydantic
class PatientCreate(BaseModel):
    email: EmailStr
    name: str
    phone: str = None


class PatientResponse(BaseModel):
    id: int
    email: str
    name: str
    phone: str = None
    
    class Config:
        from_attributes = True


@router.post("/", response_model=PatientResponse)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """Crear un nuevo paciente"""
    
    # Verificar si ya existe
    existing = db.query(Patient).filter(Patient.email == patient.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Paciente ya existe")
    
    db_patient = Patient(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    
    return db_patient


@router.get("/", response_model=List[PatientResponse])
def list_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todos los pacientes"""
    patients = db.query(Patient).offset(skip).limit(limit).all()
    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """Obtener un paciente específico"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    return patient
