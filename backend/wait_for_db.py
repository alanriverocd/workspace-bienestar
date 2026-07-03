import os
import time
import sys
import asyncpg

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@control_db:5432/postgres')

async def check():
    try:
        # read and normalize DATABASE_URL at call time
        raw = os.environ.get('DATABASE_URL', DATABASE_URL)
        if raw.startswith('postgresql+asyncpg://'):
            raw = raw.replace('postgresql+asyncpg://', 'postgresql://', 1)
        conn = await asyncpg.connect(raw)
        await conn.close()
        return True
    except Exception:
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import asyncio
    timeout = int(os.environ.get('DB_WAIT_TIMEOUT', '60'))
    interval = 1
    elapsed = 0
    while elapsed < timeout:
        # some callers set DATABASE_URL like 'postgresql+asyncpg://...' (SQLAlchemy style)
        # asyncpg expects 'postgresql://', so normalize the scheme if needed
        raw = os.environ.get('DATABASE_URL', '')
        if raw.startswith('postgresql+asyncpg://'):
            os.environ['DATABASE_URL'] = raw.replace('postgresql+asyncpg://', 'postgresql://', 1)
        ok = asyncio.run(check())
        if ok:
            print('db ready')
            sys.exit(0)
        time.sleep(interval)
        elapsed += interval
    print('db wait timeout', file=sys.stderr)
    sys.exit(1)
