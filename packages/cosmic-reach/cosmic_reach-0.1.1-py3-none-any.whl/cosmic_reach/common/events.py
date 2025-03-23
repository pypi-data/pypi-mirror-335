import asyncio
from typing import Any, Callable, Coroutine


class ListenableEvent:
    _handlers: list[Callable[..., Coroutine[Any, Any, None]]]
    _events: list[asyncio.Event]

    def __init__(self):
        self._handlers = []
        self._events = []

    def add_handler(self, handler: Callable[..., Coroutine[Any, Any, None]]) -> None:
        self._handlers.append(handler)

    def __call__(
        self, handler: Callable[..., Coroutine[Any, Any, None]]
    ) -> Callable[..., Coroutine[Any, Any, None]]:
        self.add_handler(handler)
        return handler

    async def emit(self, *args, **kwargs) -> None:
        for handler in self._handlers:
            await asyncio.get_event_loop().create_task(handler(*args, **kwargs))
        for event in self._events:
            event.set()

    async def wait_for(self):
        event = asyncio.Event()
        self._events.append(event)
        await event.wait()
        self._events.remove(event)


class FilterableListenableEvent(ListenableEvent):
    _handlers: list[tuple[Callable[..., Coroutine[Any, Any, None]], Any]]
    _events: list[tuple[asyncio.Event, Any]]

    def add_handler(
        self,
        handler: Callable[..., Coroutine[Any, Any, None]],
        filter_: Any | None = None,
    ) -> None:
        self._handlers.append((handler, filter_))

    def only(self, filter_: Any) -> Callable[
        [Callable[..., Coroutine[Any, Any, None]]],
        Callable[..., Coroutine[Any, Any, None]],
    ]:
        return lambda handler: self.add_handler(handler, filter_)

    def __call__(
        self,
        handler: Callable[..., Coroutine[Any, Any, None]],
    ) -> Callable[..., Coroutine[Any, Any, None]]:
        if callable(handler):
            self.add_handler(handler)
            return handler
        self.add_handler(handler, None)
        return handler

    async def emit(self, filter_, *args, **kwargs) -> None:
        for handler, filt_ in self._handlers:
            if filter_ is None or filt_ is None or filt_ == filter_ or filt_ is filter_:
                await asyncio.get_event_loop().create_task(handler(*args, **kwargs))
        for event, filt_ in self._events:
            if filter_ is None or filt_ is None or filt_ == filter_ or filt_ is filter_:
                event.set()

    async def wait_for(self, _filter=None):
        event = asyncio.Event()
        self._events.append((event, _filter))
        await event.wait()
        self._events.remove((event, _filter))
