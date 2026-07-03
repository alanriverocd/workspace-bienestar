import asyncio
import uuid
import datetime
import random
import argparse

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


async def create_many(total: int = 1000, batch_size: int = 100):
    """Create many sample sincronizaciones and archivos in batches."""
    await init_db()
    Session = get_sessionmaker()
    created = 0
    tipos = [TipoArchivo.ventas, TipoArchivo.inventario, TipoArchivo.clientes]
    async with Session() as session:
        while created < total:
            batch = min(batch_size, total - created)
            objs = []
            for bidx in range(batch):
                corr = uuid.uuid4()
                s = Sincronizacion(
                    correlation_id=corr,
                    fecha_ejecucion=datetime.date.today(),
                    estado=EstadoSync.completed,
                    iniciado_at=datetime.datetime.utcnow(),
                    finalizado_at=datetime.datetime.utcnow(),
                    usuario_origen='seed_many',
                )
                # add 1-3 archivos per sincronizacion
                archivos = []
                for i in range(random.randint(1, 3)):
                    # include unique piece to avoid checksum collisions
                    name = f'sample_many_{created}_{bidx}_{i}_{uuid.uuid4().hex[:8]}.csv'
                    chk = sha256_of_bytes(name.encode())
                    a = ArchivoProcesado(
                        nombre_archivo=name,
                        tipo_archivo=random.choice(tipos),
                        checksum=chk,
                        estado='accepted',
                        registros_totales=random.randint(1, 1000),
                        datos_payload={'generated': True},
                    )
                    archivos.append(a)
                # attach archivos via relationship if supported
                try:
                    s.archivos = archivos
                except Exception:
                    for a in archivos:
                        session.add(a)
                objs.append(s)
            session.add_all(objs)
            await session.commit()
            created += batch
            print(f'Created {created}/{total} sincronizaciones')


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--many', type=int, default=0, help='Create many sample records')
    p.add_argument('--batch', type=int, default=100, help='Batch size for creating records')
    return p.parse_args()


if __name__ == '__main__':
    args = _parse_args()
    if args.many and args.many > 0:
        asyncio.run(create_many(total=args.many, batch_size=args.batch))
    else:
        asyncio.run(create_sample())
