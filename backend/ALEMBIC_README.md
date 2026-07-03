Para generar la migración inicial:

1. Instalar dependencias: `pip install -r requirements.txt`
2. Desde `backend/` ejecutar:

```bash
alembic revision --autogenerate -m "init"
alembic upgrade head
```

Nota: `alembic.ini` y `alembic/env.py` están configurados para leer `DATABASE_URL` desde el entorno.
