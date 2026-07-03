from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import logging
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from .db import get_sessionmaker, init_db, get_engine
from .models import ArchivoProcesado, Sincronizacion, LogError, AccionRemediacion
from .schemas import ArchivoCreate, SincronizacionCreate, LogCreate, AccionCreate
from .utils import sha256_of_bytes, run_cpu_bound
import datetime
import asyncio
import os

app = FastAPI(title="Control y Auditoría")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("control_backend")

# CORS (allow frontend dev host)
# Allow configurable frontend origins via env var `FRONTEND_ORIGINS` (comma-separated)
default_origins = ["http://localhost:5173", "https://alanriverocd.github.io"]
raw = os.environ.get("FRONTEND_ORIGINS")
if raw:
    origins = [o.strip() for o in raw.split(',') if o.strip()]
else:
    origins = default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await init_db()


SessionLocal = get_sessionmaker()


async def get_db():
    async with SessionLocal() as session:
        yield session


@app.post("/sync")
async def create_sync(payload: SincronizacionCreate):
    async with SessionLocal() as session:
        sync = Sincronizacion(
            correlation_id=payload.correlation_id,
            fecha_ejecucion=payload.fecha_ejecucion,
            estado=payload.estado,
            iniciado_at=payload.iniciado_at,
            usuario_origen=payload.usuario_origen,
        )
        session.add(sync)
        await session.commit()
        await session.refresh(sync)
        return {"id": str(sync.id), "correlation_id": str(sync.correlation_id)}


@app.post("/files")
async def ingest_file(payload: ArchivoCreate, background_tasks: BackgroundTasks):
    async with SessionLocal() as session:
        # Idempotency: check by checksum
        q = await session.execute(select(ArchivoProcesado).where(ArchivoProcesado.checksum == payload.checksum))
        existing = q.scalars().first()
        if existing:
            return {"id": existing.id, "status": "already_processed"}

        archivo = ArchivoProcesado(
            sincronizacion_id=payload.sincronizacion_id,
            nombre_archivo=payload.nombre_archivo,
            tipo_archivo=payload.tipo_archivo,
            checksum=payload.checksum,
            registros_totales=payload.registros_totales,
            datos_payload=payload.datos_payload,
            estado="accepted",
        )
        session.add(archivo)
        try:
            await session.commit()
            await session.refresh(archivo)
        except IntegrityError:
            await session.rollback()
            q = await session.execute(select(ArchivoProcesado).where(ArchivoProcesado.checksum == payload.checksum))
            existing = q.scalars().first()
            if existing:
                return {"id": existing.id, "status": "already_processed"}
            raise HTTPException(status_code=500, detail="Integrity error")

        # Spawn background CPU-bound task to simulate parse
        async def heavy_parse(aid):
            def parse_sim(id_):
                import time
                time.sleep(0.1)
                return True

            await run_cpu_bound(parse_sim, aid)

        background_tasks.add_task(heavy_parse, archivo.id)
        return {"id": archivo.id, "status": "created"}


@app.get("/dashboard")
async def dashboard():
    async with SessionLocal() as session:
        q = await session.execute(select(Sincronizacion).options(selectinload(Sincronizacion.archivos)))
        items = q.scalars().all()
        result = []
        for s in items:
            files = [
                {"id": f.id, "nombre": f.nombre_archivo, "estado": (f.estado.value if hasattr(f.estado, 'value') else f.estado), "checksum": f.checksum, "tipo": (f.tipo_archivo.value if hasattr(f.tipo_archivo, 'value') else f.tipo_archivo)}
                for f in s.archivos
            ]
            result.append({
                "id": str(s.id),
                "correlation_id": str(s.correlation_id),
                "estado": (s.estado.value if hasattr(s.estado, 'value') else s.estado),
                "usuario_origen": s.usuario_origen,
                "archivos": files,
            })
        return {"sincronizaciones": result}


@app.get("/logs")
async def logs(q: str = None):
    async with SessionLocal() as session:
        stmt = select(LogError)
        if q:
            stmt = stmt.where(LogError.mensaje.ilike(f"%{q}%"))
        res = await session.execute(stmt)
        logs = [
            {"id": r.id, "mensaje": r.mensaje, "codigo": r.codigo_error, "nivel": (r.nivel_error.value if hasattr(r.nivel_error, 'value') else r.nivel_error)}
            for r in res.scalars().all()
        ]
        return {"logs": logs}


@app.post('/logs')
async def create_log(payload: LogCreate):
    async with SessionLocal() as session:
        log = LogError(
            correlation_id=payload.correlation_id,
            servicio_responsable=payload.servicio_responsable,
            nivel_error=payload.nivel_error,
            codigo_error=payload.codigo_error,
            mensaje=payload.mensaje,
            stack_trace=payload.stack_trace,
        )
        session.add(log)
        await session.commit()
        await session.refresh(log)
        return {"id": log.id}


@app.post('/actions')
async def create_action(payload: AccionCreate):
    async with SessionLocal() as session:
        action = AccionRemediacion(
            sincronizacion_id=payload.sincronizacion_id,
            accion_ejecutada=payload.accion_ejecutada,
            ejecutado_por=payload.ejecutado_por,
            resultado=payload.resultado,
            notas=payload.notas,
        )
        session.add(action)
        await session.commit()
        await session.refresh(action)
        return {"id": action.id}
