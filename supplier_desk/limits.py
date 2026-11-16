"""Pacing for the Gemini free tier (10 requests per minute on flash-lite)."""
import asyncio
import os
import time

MIN_GAP = float(os.environ.get("SUPPLIER_DESK_MIN_GAP_S", "7"))
_last = 0.0
_lock = asyncio.Lock()


async def pace(callback_context, llm_request):
    """before_model_callback: keep model calls at least MIN_GAP seconds apart."""
    global _last
    async with _lock:
        wait = MIN_GAP - (time.time() - _last)
        if wait > 0:
            await asyncio.sleep(wait)
        _last = time.time()
    return None
