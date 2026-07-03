import enum
import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    Date,
    TIMESTAMP,
    Text,
    ForeignKey,
    JSON,
    Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from .db import Base
from sqlalchemy import func


class EstadoSync(enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    rejected = "rejected"


class TipoArchivo(enum.Enum):
    ventas = "ventas"
    inventario = "inventario"
    clientes = "clientes"


class NivelError(enum.Enum):
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ResultadoAccion(enum.Enum):
    success = "success"
    failed = "failed"


class Sincronizacion(Base):
    __tablename__ = "sincronizaciones"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    correlation_id = Column(PG_UUID(as_uuid=True), unique=True, nullable=False, index=True, default=uuid.uuid4)
    fecha_ejecucion = Column(Date, nullable=False)
    estado = Column(SAEnum(EstadoSync, name="estado_sync"), nullable=False)
    iniciado_at = Column(TIMESTAMP, nullable=False)
    finalizado_at = Column(TIMESTAMP, nullable=True)
    usuario_origen = Column(String(100))

    archivos = relationship("ArchivoProcesado", back_populates="sincronizacion", cascade="all, delete")
    acciones = relationship("AccionRemediacion", back_populates="sincronizacion", cascade="all, delete")


class ArchivoProcesado(Base):
    __tablename__ = "archivos_procesados"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sincronizacion_id = Column(PG_UUID(as_uuid=True), ForeignKey("sincronizaciones.id", ondelete="CASCADE"))
    nombre_archivo = Column(String(255), nullable=False)
    tipo_archivo = Column(SAEnum(TipoArchivo, name="tipo_archivo"), nullable=False)
    checksum = Column(String(64), nullable=False, unique=True)
    estado = Column(String(20))
    registros_totales = Column(Integer, default=0)
    datos_payload = Column(JSONB)

    sincronizacion = relationship("Sincronizacion", back_populates="archivos")


class LogError(Base):
    __tablename__ = "logs_errores"
    id = Column(Integer, primary_key=True, autoincrement=True)
    correlation_id = Column(PG_UUID(as_uuid=True), ForeignKey("sincronizaciones.correlation_id", ondelete="CASCADE"), index=True)
    servicio_responsable = Column(String(100))
    nivel_error = Column(SAEnum(NivelError, name="nivel_error"))
    codigo_error = Column(String(50))
    mensaje = Column(Text, nullable=False)
    stack_trace = Column(Text)
    creado_at = Column(TIMESTAMP, server_default=func.now())


class AccionRemediacion(Base):
    __tablename__ = "acciones_remediacion"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sincronizacion_id = Column(PG_UUID(as_uuid=True), ForeignKey("sincronizaciones.id", ondelete="CASCADE"))
    accion_ejecutada = Column(String(100))
    ejecutado_por = Column(String(100), nullable=False)
    resultado = Column(SAEnum(ResultadoAccion, name="resultado_accion"))
    notas = Column(Text)

    sincronizacion = relationship("Sincronizacion", back_populates="acciones")
