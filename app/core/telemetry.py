from __future__ import annotations

from time import perf_counter


class Timer:
    def __enter__(self) -> Timer:
        self._start = perf_counter()
        self.elapsed = 0.0
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.elapsed = perf_counter() - self._start
