import hashlib
from concurrent.futures import ThreadPoolExecutor
import asyncio


def sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


async def run_cpu_bound(func, *args):
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, func, *args)
