import logging
import os
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from pymongo import MongoClient
from pymongo.errors import PyMongoError


# Registros visibles en Vercel Runtime Logs
logger = logging.getLogger("uvicorn.error")

# --------------------------------------------------------------------------
# CONFIGURACIÓN DE VARIABLES DE ENTORNO
# --------------------------------------------------------------------------
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    logger.critical("No se configuró la variable MONGO_URI")
    raise RuntimeError("Falta configurar MONGO_URI en el servidor")

# Lectura directa y estricta de FRONTEND_ORIGINS sin valores por defecto estáticos
frontend_origins_raw = os.getenv("FRONTEND_ORIGINS", "")

if not frontend_origins_raw:
    logger.warning("FRONTEND_ORIGINS no está definida. Se rechazará el acceso por CORS.")
    origenes = []
else:
    # Separa por comas, elimina espacios y barras finales (ej: "http://localhost:8100,https://tu-app.vercel.app")
    origenes = [
        origen.strip().rstrip("/")
        for origen in frontend_origins_raw.split(",")
        if origen.strip()
    ]

# --------------------------------------------------------------------------
# CONEXIÓN A MONGODB ATLAS (OPTIMIZADA PARA ENTORNO SERVERLESS)
# --------------------------------------------------------------------------
client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
    socketTimeoutMS=5000,
    appName="CompruebameEcofirma",
)

db = client["compruebame_db"]
coleccion_contactos = db["contactos"]

# --------------------------------------------------------------------------
# INICIALIZACIÓN DE FASTAPI Y CONFIGURACIÓN DE CORS
# --------------------------------------------------------------------------
app = FastAPI(
    title="API Compruebame Ecofirma",
    version="1.0.0",
    description="Backend oficial para procesamiento de formularios y servicios regulatorios"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------------
# MODELO DE DATOS CON VALIDACIÓN ESTRICUTA (PYDANTIC V2)
# --------------------------------------------------------------------------
class ContactoSchema(BaseModel):
    nombre: str = Field(min_length=3, max_length=100)
    correo: EmailStr
    telefono: str = Field(pattern=r"^[0-9]{10}$")
    mensaje: str = Field(min_length=10, max_length=3000)

# --------------------------------------------------------------------------
# ENDPOINTS
# --------------------------------------------------------------------------
@app.get("/", status_code=status.HTTP_200_OK)
def read_root():
    return {
        "status": "API en línea",
        "empresa": "Compruebame Ecofirma",
    }


@app.get("/health", status_code=status.HTTP_200_OK)
def comprobar_salud():
    """
    Comprueba que la función en Vercel mantenga comunicación activa con MongoDB Atlas.
    """
    try:
        db.command("ping")
        return {
            "status": "ok",
            "database": "connected",
        }
    except PyMongoError as exc:
        logger.exception("Falló la comprobación de conexión con MongoDB Atlas")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La base de datos no está disponible temporalmente",
        ) from exc


@app.post("/api/contacto", status_code=status.HTTP_201_CREATED)
def guardar_contacto(contacto: ContactoSchema):
    """
    Procesa, valida y guarda las solicitudes del formulario en MongoDB Atlas.
    """
    try:
        # Reemplazo de .dict() por .model_dump() (Estándar oficial Pydantic V2)
        nuevo_contacto = contacto.model_dump()
        nuevo_contacto["fecha_registro"] = datetime.now(timezone.utc)

        resultado = coleccion_contactos.insert_one(nuevo_contacto)

        logger.info(f"Registro insertado exitosamente ID: {resultado.inserted_id}")

        return {
            "mensaje": "Solicitud guardada correctamente",
            "id": str(resultado.inserted_id),
        }

    except PyMongoError as exc:
        logger.exception("Error al insertar el contacto en MongoDB Atlas")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible guardar la solicitud. Intenta más tarde.",
        ) from exc