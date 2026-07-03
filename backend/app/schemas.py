from pydantic import BaseModel
from typing import Optional, Any
import datetime
import uuid


class SincronizacionCreate(BaseModel):
    correlation_id: uuid.UUID
    fecha_ejecucion: datetime.date
    estado: str
    iniciado_at: datetime.datetime
    usuario_origen: Optional[str]


class ArchivoCreate(BaseModel):
    sincronizacion_id: uuid.UUID
    nombre_archivo: str
    tipo_archivo: str
    checksum: str
    registros_totales: Optional[int] = 0
    datos_payload: Optional[Any]


class LogCreate(BaseModel):
    correlation_id: uuid.UUID
    servicio_responsable: Optional[str]
    nivel_error: Optional[str]
    codigo_error: Optional[str]
    mensaje: str
    stack_trace: Optional[str]


class AccionCreate(BaseModel):
    sincronizacion_id: uuid.UUID
    accion_ejecutada: str
    ejecutado_por: str
    resultado: str
    notas: Optional[str]
