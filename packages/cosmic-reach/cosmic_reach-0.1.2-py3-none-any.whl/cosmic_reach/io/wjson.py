from typing import Any


class MutableString:
    def __init__(self, content: str):
        self.content = content

    def has(self) -> bool:
        return bool(self.content)

    def getfirst(self) -> str:
        return self.content[0]

    def popfirst(self) -> str:
        first = self.getfirst()
        self.content = self.content[1:]
        return first

    def popuntil(self, *symbols: str) -> str:
        idx = min(
            filter(
                lambda idx: idx != -1,
                [len(self.content)] + [self.content.find(symbol) for symbol in symbols],
            )
        )
        sub = self.content[:idx]
        self.content = self.content[idx:]
        return sub


def collect(data: MutableString, *, ends: tuple[str] = tuple()) -> Any:
    if data.getfirst() == "{":
        result = {}
        while data.getfirst() != "}":
            data.popfirst()
            key = data.popuntil(":")
            data.popfirst()
            value = collect(data, ends=(",", "}"))
            result[key] = value
        data.popfirst()
        return result
    elif (start := data.getfirst()) in ("'", '"'):
        data.popfirst()
        read = data.popuntil(start)
        data.popfirst()
        return read
    else:
        read: str = data.popuntil(*ends)
        if read == "null":
            return None
        elif read == "true":
            return True
        elif read == "false":
            return False
        elif read.isdigit():
            return int(read)
        elif read.isdecimal():
            return float(read)
        return read


def loads(json_str: str) -> Any:
    d = collect(MutableString(json_str))
    return d


def dumps(obj: Any) -> str:
    if isinstance(obj, dict):
        return f"{",".join(dumps(key)+":"+dumps(value) for key, value in obj.items())}"
    elif isinstance(obj, int):
        return str(obj)
    elif isinstance(obj, str):
        return obj
    else:
        raise TypeError(f"Unsupported type {type(obj)}")
