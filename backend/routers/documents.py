from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from pathlib import Path
import mimetypes

from database import get_db
from models import Document, Patient
from config import settings

router = APIRouter(prefix="/api/documents", tags=["documents"])


class DocumentInfo(BaseModel):
    """Información de un documento"""
    id: int
    title: str
    file_type: Optional[str]
    uploaded_at: str
    download_link: Optional[str] = None
    
    class Config:
        from_attributes = True


class DownloadLinkRequest(BaseModel):
    """Solicitud de enlace de descarga seguro"""
    document_id: int
    patient_id: int


class DownloadLinkResponse(BaseModel):
    """Respuesta con enlace de descarga seguro"""
    document_id: int
    title: str
    download_url: str
    expires_in_minutes: int
    message: str


def create_download_token(document_id: int, patient_id: int) -> str:
    """Crea un token JWT para descarga de documento válido por 15 minutos"""
    payload = {
        "document_id": document_id,
        "patient_id": patient_id,
        "exp": datetime.utcnow() + timedelta(minutes=settings.DOWNLOAD_TOKEN_EXPIRE_MINUTES),
        "type": "download"
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


def verify_download_token(token: str) -> dict:
    """Verifica un token de descarga y devuelve su payload"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "download":
            raise HTTPException(status_code=401, detail="Token inválido")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expirado o inválido")


# Crear directorio de uploads si no existe
def ensure_uploads_dir():
    """Asegura que la carpeta de uploads existe"""
    upload_path = Path(settings.UPLOADS_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


@router.get("/patient/{patient_id}", response_model=List[DocumentInfo])
async def get_patient_documents(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene todos los documentos de un paciente sin enlaces de descarga"""
    # Verificar que el paciente existe
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    # Obtener documentos
    documents = db.query(Document).filter(
        Document.patient_id == patient_id
    ).order_by(Document.uploaded_at.desc()).all()
    
    result = []
    for doc in documents:
        result.append(DocumentInfo(
            id=doc.id,
            title=doc.title,
            file_type=doc.file_type,
            uploaded_at=doc.uploaded_at.isoformat() if doc.uploaded_at else None,
            download_link=None
        ))
    
    return result


@router.post("/generate-download-link", response_model=DownloadLinkResponse)
async def generate_download_link(
    request: DownloadLinkRequest,
    db: Session = Depends(get_db)
):
    """
    Genera un enlace seguro para descargar un documento.
    El enlace incluye un token JWT válido por 15 minutos.
    """
    # Verificar que el documento existe
    document = db.query(Document).filter(
        Document.id == request.document_id,
        Document.patient_id == request.patient_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=404,
            detail="Documento no encontrado o no tienes acceso a él"
        )
    
    # Generar token de descarga
    token = create_download_token(request.document_id, request.patient_id)
    
    # Construir URL de descarga
    download_url = f"/api/documents/download/{request.document_id}?token={token}"
    
    return DownloadLinkResponse(
        document_id=request.document_id,
        title=document.title,
        download_url=download_url,
        expires_in_minutes=settings.DOWNLOAD_TOKEN_EXPIRE_MINUTES,
        message=f"Enlace seguro generado. Válido por {settings.DOWNLOAD_TOKEN_EXPIRE_MINUTES} minutos. Puedes hacer la descarga ahora."
    )


@router.get("/download/{document_id}")
async def download_document(
    document_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    """
    Descarga un documento usando un token de descarga válido.
    Ejemplo: GET /api/documents/download/1?token=<jwt_token>
    """
    # Verificar token
    payload = verify_download_token(token)
    
    # Verificar que el documento_id del token coincide
    if payload.get("document_id") != document_id:
        raise HTTPException(status_code=403, detail="Token no válido para este documento")
    
    # Obtener documento de la BD
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.patient_id == payload.get("patient_id")
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    # Verificar que el archivo existe
    file_path = Path(document.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado en el servidor")
    
    # Detectar tipo MIME
    media_type, _ = mimetypes.guess_type(str(file_path))
    if not media_type:
        media_type = "application/octet-stream"
    
    # Retornar archivo
    return FileResponse(
        path=file_path,
        filename=document.title if '.' not in document.title else document.title,
        media_type=media_type
    )


@router.post("/upload/{patient_id}")
async def upload_document(
    patient_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Sube un documento médico.
    Solo uso interno de demostración.
    """
    # Verificar que el paciente existe
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    # Asegurar directorio de uploads
    uploads_dir = ensure_uploads_dir()
    
    # Generar nombre único para el archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = Path(file.filename).suffix
    safe_filename = f"{patient_id}_{timestamp}{file_extension}"
    file_path = uploads_dir / safe_filename
    
    # Guardar archivo
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar archivo: {str(e)}")
    
    # Crear registro en BD
    file_type = file_extension.lstrip(".").upper() if file_extension else "Unknown"
    document = Document(
        patient_id=patient_id,
        title=file.filename,
        file_path=str(file_path),
        file_type=file_type
    )
    
    try:
        db.add(document)
        db.commit()
        db.refresh(document)
    except Exception as e:
        # Eliminar archivo si falló la BD
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")
    
    return {
        "message": "Documento subido exitosamente",
        "document_id": document.id,
        "filename": file.filename,
        "file_type": file_type
    }
