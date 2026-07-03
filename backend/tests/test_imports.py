import uuid
import datetime


def test_module_imports_and_schemas():
    import app.main as main
    import app.db as db
    import app.models as models
    import app.schemas as schemas
    import app.utils as utils

    # basic attributes exist
    assert hasattr(main, "app")
    assert callable(db.get_engine)

    # instantiate pydantic schemas
    s = schemas.SincronizacionCreate(
        correlation_id=uuid.uuid4(),
        fecha_ejecucion=datetime.date.today(),
        estado="pending",
        iniciado_at=datetime.datetime.utcnow(),
        usuario_origen="tester",
    )
    a = schemas.ArchivoCreate(
        sincronizacion_id=uuid.uuid4(),
        nombre_archivo="archivo.csv",
        tipo_archivo="ventas",
        checksum="abc123",
        registros_totales=10,
    )

    assert s.estado == "pending"
    assert a.checksum == "abc123"
