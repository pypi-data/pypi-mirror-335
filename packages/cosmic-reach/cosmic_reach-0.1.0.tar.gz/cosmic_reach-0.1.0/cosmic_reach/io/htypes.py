class KeyedUnion[T]:
    def __init__(self, **kwargs: dict[str, T]):
        self._e = kwargs
