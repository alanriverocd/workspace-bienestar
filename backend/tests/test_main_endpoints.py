import uuid
import datetime
from fastapi.testclient import TestClient


class QueryResult:
    def __init__(self, rows=None):
        self._rows = rows or []

    def scalars(self):
        return self

    def first(self):
        return None if not self._rows else self._rows[0]

    def all(self):
        return list(self._rows)


class FakeSession:
    def __init__(self):
        self._next_int = 1

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def execute(self, stmt):
        return QueryResult([])

    def add(self, obj):
        # attach a provisional id for SQLAlchemy model objects
        try:
            if hasattr(obj, 'id') and obj.id is None:
                obj.id = self._next_int
                self._next_int += 1
        except Exception:
            pass

    async def commit(self):
        return True

    async def refresh(self, obj):
        # ensure id exists
        import uuid

        if not getattr(obj, 'id', None):
            try:
                obj.id = uuid.uuid4()
            except Exception:
                obj.id = 1

    async def rollback(self):
        return True


def test_endpoints_monkeypatched(monkeypatch):
    import app.main as main

    async def noop_init():
        return None

    monkeypatch.setattr(main, 'init_db', noop_init)
    monkeypatch.setattr(main, 'SessionLocal', lambda: FakeSession())

    client = TestClient(main.app)

    # POST /sync
    payload = {
        "correlation_id": str(uuid.uuid4()),
        "fecha_ejecucion": datetime.date.today().isoformat(),
        "estado": "pending",
        "iniciado_at": datetime.datetime.utcnow().isoformat(),
        "usuario_origen": "tester",
    }
    r = client.post('/sync', json=payload)
    assert r.status_code == 200
    assert 'id' in r.json()

    # POST /files (ingest)
    payload_file = {
        "sincronizacion_id": str(uuid.uuid4()),
        "nombre_archivo": "f.csv",
        "tipo_archivo": "ventas",
        "checksum": "chk123",
        "registros_totales": 1,
    }
    r2 = client.post('/files', json=payload_file)
    assert r2.status_code == 200
    assert r2.json().get('status') in ('created', 'already_processed')

    # GET /dashboard
    r3 = client.get('/dashboard')
    assert r3.status_code == 200
    assert 'sincronizaciones' in r3.json()

    # GET /logs
    r4 = client.get('/logs')
    assert r4.status_code == 200
    assert 'logs' in r4.json()

    # POST /logs
    payload_log = {
        "correlation_id": str(uuid.uuid4()),
        "mensaje": "error prueba",
    }
    r5 = client.post('/logs', json=payload_log)
    assert r5.status_code == 200
    assert 'id' in r5.json()

    # POST /actions
    payload_act = {
        "sincronizacion_id": str(uuid.uuid4()),
        "accion_ejecutada": "fix",
        "ejecutado_por": "sys",
        "resultado": "success",
    }
    r6 = client.post('/actions', json=payload_act)
    assert r6.status_code == 200
    assert 'id' in r6.json()
