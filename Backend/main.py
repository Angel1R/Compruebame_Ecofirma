from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
import datetime
import os

app = FastAPI(title="API Compruebame Ecofirma")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Leer la credencial de forma segura desde el servidor
MONGO_URI = os.getenv("MONGO_URI")

try:
    client = MongoClient(MONGO_URI)
    db = client["compruebame_db"]
    coleccion_contactos = db["contactos"]
    print("Conexión exitosa a MongoDB Atlas")
except Exception as e:
    print(f"Error al conectar con MongoDB: {e}")

class ContactoSchema(BaseModel):
    nombre: str
    correo: str
    telefono: str
    mensaje: str

@app.get("/")
def read_root():
    return {"status": "API en línea", "empresa": "Compruebame Ecofirma"}

@app.post("/api/contacto", status_code=status.HTTP_201_CREATED)
def guardar_contacto(contacto: ContactoSchema):
    try:
        nuevo_contacto = contacto.dict()
        nuevo_contacto["fecha_registro"] = datetime.datetime.utcnow()
        
        resultado = coleccion_contactos.insert_one(nuevo_contacto)
        
        return {
            "mensaje": "Solicitud guardada correctamente",
            "id": str(resultado.inserted_id)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al guardar en la base de datos: {str(e)}"
        )