import os
import asyncio
import subprocess

import asyncpg

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@control_db:5432/postgres")
if DATABASE_URL.startswith('postgresql+asyncpg://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')

async def main():
    try:
        conn = await asyncpg.connect(DATABASE_URL)
    except Exception as e:
        print('DB connection failed:', e)
        raise
    try:
        exists = await conn.fetchval("SELECT to_regclass('public.sincronizaciones')")
        if exists:
            print('Schema detected. Stamping Alembic head (no DDL will be run).')
            subprocess.run(['alembic', 'stamp', 'head'], check=True)
        else:
            print('No schema found. Running alembic upgrade head (will apply DDL).')
            subprocess.run(['alembic', 'upgrade', 'head'], check=True)
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(main())
