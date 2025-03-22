from enum import IntEnum

class DDRPin(IntEnum):
    DDRA = 0x21,
    DDA0 = 0,
    DDA1 = 1,
    DDA2 = 2,
    DDA3 = 3,
    DDA4 = 4,
    DDA5 = 5,
    DDA6 = 6,
    DDA7 = 7,

class PortPin(IntEnum):
    PORTA    = 0x21,
    PORTA0   = 0,
    PORTA1   = 1,
    PORTA2   = 2,
    PORTA3   = 3,
    PORTA4   = 4,
    PORTA5   = 5,
    PORTA6   = 6,
    PORTA7   = 7,

class PinPin(IntEnum):
    PINA  = 0x21,
    PINA0 = 0,
    PINA1 = 1,
    PINA2 = 2,
    PINA3 = 3,
    PINA4 = 4,
    PINA5 = 5,
    PINA6 = 6,
    PINA7 = 7,
