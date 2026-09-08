from collections import defaultdict, deque
from time import time


class InMemoryRateLimiter:
    def __init__(self, limit: int, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self.hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time()
        q = self.hits[key]
        while q and now - q[0] > self.window_seconds:
            q.popleft()
        if len(q) >= self.limit:
            return False
        q.append(now)
        return True
