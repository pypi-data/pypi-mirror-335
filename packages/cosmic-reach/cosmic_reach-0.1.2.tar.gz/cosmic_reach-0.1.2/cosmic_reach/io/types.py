import io
import json
import struct
from enum import Enum
from typing import Any, Union

from dataclasses_json import DataClassJsonMixin

from . import wjson
from .htypes import KeyedUnion
from .serializer import deserialize, deserializer_for, serialize, serializer_for


def consuming_unpack(format_: str, buf: io.BytesIO) -> tuple:
    return struct.unpack(format_, buf.read(struct.calcsize(format_)))


class Byte(int):
    pass


class UByte(int):
    pass


class Short(int):
    pass


class Long(int):
    pass


class Double(int):
    pass


class Complex:
    def __init__(self, *args, **kwargs):
        for key, val in zip(type(self).__annotations__.keys(), args):
            setattr(self, key, val)

        for key, val in kwargs.items():
            setattr(self, key, val)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


class _Repeat:
    _t: type

    def __init__(self, item):
        self._t = item


class _RepeatMeta(type):
    def __getitem__(self, item):
        return _Repeat(item)


class Repeat(list, metaclass=_RepeatMeta): ...


class _Tuple:
    _t: tuple[type]

    def __init__(self, item):
        self._t = item


class _TupleMeta(type):
    def __getitem__(self, item):
        return _Tuple(item)


class Tuple(tuple, metaclass=_TupleMeta): ...


@serializer_for(Byte)
@serializer_for(bool)
def serialize_byte[T: Byte | bool](typ: type[T], num: T) -> bytes:
    return num.to_bytes(1, "big", signed=True)


@deserializer_for(Byte)
@deserializer_for(bool)
def deserialize_byte[T: Byte | bool](typ: type[T], buf: io.BytesIO) -> T:
    return Short.from_bytes(buf.read(1), "big", signed=True)


@serializer_for(UByte)
def serialize_ubyte[T: UByte](typ: type[T], num: T) -> bytes:
    return num.to_bytes(1, "big", signed=False)


@deserializer_for(UByte)
def deserialize_ubyte[T: UByte](typ: type[T], buf: io.BytesIO) -> T:
    return Short.from_bytes(buf.read(1), "big", signed=False)


@serializer_for(Short)
def serialize_short[T: Short](typ: type[T], num: T) -> bytes:
    return num.to_bytes(2, "big", signed=True)


@deserializer_for(Short)
def deserialize_short[T: Short](typ: type[T], buf: io.BytesIO) -> T:
    return Short.from_bytes(buf.read(2), "big", signed=True)


@serializer_for(Long)
def serialize_long[T: Long](typ: type[T], num: T) -> bytes:
    return num.to_bytes(8, "big", signed=True)


@deserializer_for(Long)
def deserialize_long[T: Long](typ: type[T], buf: io.BytesIO) -> T:
    return Long.from_bytes(buf.read(8), "big", signed=True)


@serializer_for(int)
def serialize_int[T: int](typ: type[T], num: T) -> bytes:
    return num.to_bytes(4, "big", signed=True)


@deserializer_for(int)
def deserialize_int[T: int](typ: type[T], buf: io.BytesIO) -> T:
    return int.from_bytes(buf.read(4), "big", signed=True)


@serializer_for(Double)
def serialize_double[T: Double](typ: type[T], num: T) -> bytes:
    return struct.pack(">d", num)


@deserializer_for(Double)
def deserialize_double[T: Double](typ: type[T], buf: io.BytesIO) -> T:
    return Double(consuming_unpack(">d", buf)[0])


@serializer_for(float)
def serialize_float[T: float](typ: type[T], num: T) -> bytes:
    return struct.pack(">f", num)


@deserializer_for(float)
def deserialize_float[T: float](typ: type[T], buf: io.BytesIO) -> T:
    return consuming_unpack(">f", buf)[0]


@serializer_for(bytes)
def serialize_bytes[T: bytes](typ: type[T], byt: T) -> bytes:
    return serialize_int(int, len(byt)) + byt


@deserializer_for(bytes)
def deserialize_bytes[T: bytes](typ: type[T], buf: io.BytesIO) -> T:
    length = deserialize_int(int, buf)
    return buf.read(length)


@serializer_for(str)
def serialize_str[T: str](typ: type[T], string: T) -> bytes:
    return serialize_bytes(bytes, string.encode("utf-8"))


@deserializer_for(str)
def deserialize_str[T: str](typ: type[T], buf: io.BytesIO) -> T:
    return deserialize_bytes(bytes, buf).decode("utf-8")


@serializer_for(_Repeat)
def serialize_arr[T: Repeat](typ: type[T], vals: T) -> bytes:
    return serialize_int(int, len(vals)) + b"".join(
        serialize(val, typ._t) for val in vals
    )


@deserializer_for(_Repeat)
def deserialize_arr[T: Repeat](typ: type[T], buf: io.BytesIO) -> T:
    length = deserialize_int(int, buf)
    return [deserialize(typ._t, buf) for _ in range(length)]


@serializer_for(_Tuple)
def serialize_tup[T: Tuple](typ: type[T], vals: T) -> bytes:
    return b"".join(serialize(val, subtyp) for val, subtyp in zip(vals, typ._t))


@deserializer_for(_Tuple)
def deserialize_tup[T: Tuple](typ: type[T], buf: io.BytesIO) -> T:
    return [deserialize(subtyp, buf) for subtyp in typ._t]


@serializer_for(dict)
def serialize_json[T: dict](typ: type[T], json_: T) -> bytes:
    return serialize_str(str, json.dumps(json_))


@deserializer_for(dict)
def deserialize_json[T: dict](typ: type[T], buf: io.BytesIO) -> T:
    return wjson.loads(deserialize_str(str, buf))


@serializer_for(DataClassJsonMixin)
def serialize_dataclass[T: DataClassJsonMixin](typ: type[T], dataclass: T) -> bytes:
    return serialize_json(dict, dataclass.to_dict())


@deserializer_for(DataClassJsonMixin)
def deserialize_dataclass[T: DataClassJsonMixin](typ: type[T], buf: io.BytesIO) -> T:
    return typ.from_dict(deserialize_json(dict, buf))


@serializer_for(Complex)
def serialize_complex[T: Complex](typ: type[T], complex: T) -> bytes:
    all_annotations = complex.__annotations__
    for base in typ.__bases__:
        all_annotations.update(base.__annotations__)

    result = b""

    for attr, subtyp in all_annotations.items():
        if not hasattr(complex, attr):
            raise ValueError(f"Missing attribute {attr} in {complex}")

        result += serialize(getattr(complex, attr), subtyp)
    return result


@deserializer_for(Complex)
def deserialize_complex[T: Complex](typ: type[T], buf: io.BytesIO) -> T:
    all_annotations = typ.__annotations__
    for base in typ.__bases__:
        all_annotations.update(base.__annotations__)

    result = {}

    for attr, subtyp in all_annotations.items():
        result[attr] = deserialize(subtyp, buf)

    return typ.from_dict(result)


@serializer_for(Union)
def serialize_union[T: Union](typ: type[T], uni: T) -> bytes:
    for idx, subtyp in enumerate(typ.__args__):
        if isinstance(uni, subtyp):
            break
    else:
        raise ValueError(f"Invalid type {type(uni)} for {typ}")

    return serialize_byte(Byte, idx) + serialize(uni, subtyp)


@deserializer_for(Union)
def deserialize_union[T: Union](typ: type[T], buf: io.BytesIO) -> T:
    idx = deserialize_byte(Byte, buf)
    return deserialize(typ.__args__[idx], buf)


@serializer_for(Enum)
def serialize_enum[T: Enum](typ: type[T], enm: T) -> bytes:
    return serialize_byte(UByte, enm.value)


@deserializer_for(Enum)
def deserialize_enum[T: Enum](typ: type[T], buf: io.BytesIO) -> T:
    idx = deserialize_byte(UByte, buf)
    return typ(idx)


@serializer_for(KeyedUnion)
def serialize_keyed_union[T: Any](typ: KeyedUnion, uni: T) -> bytes:
    for key, subtyp in typ._e.items():
        print(subtyp, uni)
        if isinstance(uni, subtyp):
            break
    else:
        raise ValueError(f"Invalid type {type(uni)} for {typ}")

    return serialize_str(str, key) + serialize(uni, subtyp)


@deserializer_for(KeyedUnion)
def deserialize_keyed_union[T: Any](typ: KeyedUnion, buf: io.BytesIO) -> T:
    key = deserialize_str(str, buf)
    return deserialize(typ._e[key], buf)
