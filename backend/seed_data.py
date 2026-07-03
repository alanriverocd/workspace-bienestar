import asyncio
import uuid
import datetime

from app.db import get_sessionmaker, init_db
from app.models import Sincronizacion, ArchivoProcesado, LogError, AccionRemediacion, EstadoSync, TipoArchivo, NivelError, ResultadoAccion
from app.utils import sha256_of_bytes


async def create_sample():
    # ensure DB schema exists
    await init_db()
    Session = get_sessionmaker()
    async with Session() as session:
        # create a sincronizacion
        corr = uuid.uuid4()
        s = Sincronizacion(
            correlation_id=corr,
            fecha_ejecucion=datetime.date.today(),
            estado=EstadoSync.completed,
            iniciado_at=datetime.datetime.utcnow(),
            finalizado_at=datetime.datetime.utcnow(),
            usuario_origen='seed_script',
        )
        session.add(s)
        await session.commit()
        await session.refresh(s)

        # add some archivos
        files = []
        for i, t in enumerate([TipoArchivo.ventas, TipoArchivo.inventario, TipoArchivo.clientes], start=1):
            name = f'sample_{i}.csv'
            chk = sha256_of_bytes(name.encode())
            a = ArchivoProcesado(
                sincronizacion_id=s.id,
                nombre_archivo=name,
                tipo_archivo=t,
                checksum=chk,
                estado='accepted',
                registros_totales=10 * i,
                datos_payload={'sample': True, 'rows': 10 * i},
            )
            session.add(a)
            files.append(a)

        # create an error log
        log = LogError(
            correlation_id=corr,
            servicio_responsable='Validation_Engine',
            nivel_error=NivelError.ERROR,
            codigo_error='ERR_SAMPLE_001',
            mensaje='Sample error inserted by seed script',
            stack_trace=None,
        )
        session.add(log)

        # create an action
        act = AccionRemediacion(
            sincronizacion_id=s.id,
            accion_ejecutada='RETRY_JOB',
            ejecutado_por='seed_operator',
            resultado=ResultadoAccion.success,
            notas='Seed action executed',
        )
        session.add(act)

        await session.commit()

        print('Seed completed: sincronizacion id=', s.id)


if __name__ == '__main__':
    asyncio.run(create_sample())
