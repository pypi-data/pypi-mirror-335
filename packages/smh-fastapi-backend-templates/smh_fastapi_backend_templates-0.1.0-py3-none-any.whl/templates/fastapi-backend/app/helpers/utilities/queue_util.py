from collections import deque
import asyncio

document_queue = deque()
queue_lock = asyncio.Lock()

BATCH_SIZE = 1000
FLUSH_INTERVAL = 5

async def add_to_queue(record:dict):
    async with queue_lock:
        document_queue.append(record)

async def get_queue_records():
    async with queue_lock:
        batch=[]
        if document_queue:
            batch = list(document_queue)
            document_queue.clear()
        return batch
async def process_queue(callback_func):
    batch = get_queue_records()
    if batch:
        await callback_func(batch)
async def flush_queue(callback_func):
    while True:
        await asyncio.sleep(FLUSH_INTERVAL)
        await process_queue(callback_func)