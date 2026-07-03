import os
import time
import sys
import asyncpg

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@control_db:5432/postgres')

async def check():
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.close()
        return True
    except Exception:
        return False

if __name__ == '__main__':
    import asyncio
    timeout = int(os.environ.get('DB_WAIT_TIMEOUT', '60'))
    interval = 1
    elapsed = 0
    while elapsed < timeout:
        ok = asyncio.run(check())
        if ok:
            print('db ready')
            sys.exit(0)
        time.sleep(interval)
        elapsed += interval
    print('db wait timeout', file=sys.stderr)
    sys.exit(1)
