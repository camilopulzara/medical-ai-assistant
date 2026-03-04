#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para iniciar el backend con encoding UTF-8 correcto
Usa este script en lugar de main.py directamente
"""

import os
import sys
import io

# Configurar encoding UTF-8 ANTES de cualquier otra cosa
os.environ['PYTHONIOENCODING'] = 'utf-8'

if sys.stdout:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr:
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Ahora importar FastAPI y otros módulos
import uvicorn
from main import app

if __name__ == "__main__":
    print("=" * 60)
    print("INICIANDO BACKEND CON ENCODING UTF-8")
    print("=" * 60)
    
    # Usar la forma correcta para uvicorn con reload
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )
