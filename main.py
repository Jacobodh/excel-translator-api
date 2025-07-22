from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List
import os

from excel_utils import guardar_archivo_temporal, extraer_celdas_con_texto, escribir_excel_traducido

app = FastAPI()

# Base de datos temporal en memoria
archivos_guardados = {}

class Traduccion(BaseModel):
    row: int
    col: int
    texto: str

class TraduccionRequest(BaseModel):
    archivo_id: str
    traducciones: List[Traduccion]

@app.post("/extraer_texto")
async def extraer_texto(file: UploadFile = File(...)):
    filepath = guardar_archivo_temporal(file)
    archivo_id = os.path.basename(filepath)
    archivos_guardados[archivo_id] = filepath

    celdas = extraer_celdas_con_texto(filepath)
    return JSONResponse(content={
        "archivo_id": archivo_id,
        "celdas": celdas
    })

@app.post("/escribir_traduccion")
async def escribir_traduccion(request: TraduccionRequest):
    archivo_id = request.archivo_id
    if archivo_id not in archivos_guardados:
        return JSONResponse(status_code=404, content={"error": "Archivo no encontrado"})

    ruta_archivo = archivos_guardados[archivo_id]
    archivo_salida = escribir_excel_traducido(ruta_archivo, request.traducciones)
    return FileResponse(archivo_salida, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")