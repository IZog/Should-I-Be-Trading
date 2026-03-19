from __future__ import annotations

import asyncio
import time
from typing import Any, Callable, Coroutine


class MarketCache:
    def __init__(self, ttl: int = 30):
        self.ttl = ttl
        self.data: dict[str, Any] = {}
        self.last_fetched: float = 0.0
        self.lock = asyncio.Lock()

    async def get_or_fetch(
        self, key: str, fetch_fn: Callable[[], Coroutine[Any, Any, Any]]
    ) -> Any:
        now = time.time()
        if key in self.data and (now - self.last_fetched) < self.ttl:
            return self.data[key]

        async with self.lock:
            # Double-check after acquiring lock
            now = time.time()
            if key in self.data and (now - self.last_fetched) < self.ttl:
                return self.data[key]

            result = await fetch_fn()
            self.data[key] = result
            self.last_fetched = time.time()
            return result

    def invalidate(self, key: str | None = None) -> None:
        if key is None:
            self.data.clear()
            self.last_fetched = 0.0
        elif key in self.data:
            del self.data[key]
            self.last_fetched = 0.0


market_cache = MarketCache()
