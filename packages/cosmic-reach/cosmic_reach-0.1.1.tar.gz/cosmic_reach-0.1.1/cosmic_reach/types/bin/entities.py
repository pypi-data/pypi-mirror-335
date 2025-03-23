from ...io.types import Complex, Long


class UniqueID(Complex):
    time: Long
    rand: int
    number: int
