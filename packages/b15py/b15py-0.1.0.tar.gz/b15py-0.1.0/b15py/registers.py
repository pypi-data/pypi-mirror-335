from enum import IntEnum

class DDRPin(IntEnum):
    DDRA = 0x21,
    DDRA0 = 0,
    DDRA1 = 1,
    DDRA2 = 2,
    DDRA3 = 3,
    DDRA4 = 4,
    DDRA5 = 5,
    DDRA6 = 6,
    DDRA7 = 7,

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

DDRA = DDRPin.DDRA
DDRA0 = DDRPin.DDRA0
DDRA1 = DDRPin.DDRA1
DDRA2 = DDRPin.DDRA2
DDRA3 = DDRPin.DDRA3
DDRA4 = DDRPin.DDRA4
DDRA5 = DDRPin.DDRA5
DDRA6 = DDRPin.DDRA6
DDRA7 = DDRPin.DDRA7

PORTA = PortPin.PORTA
PORTA0 = PortPin.PORTA0
PORTA1 = PortPin.PORTA1
PORTA2 = PortPin.PORTA2
PORTA3 = PortPin.PORTA3
PORTA4 = PortPin.PORTA4
PORTA5 = PortPin.PORTA5
PORTA6 = PortPin.PORTA6
PORTA7 = PortPin.PORTA7

PINA = PinPin.PINA
PINA0 = PinPin.PINA0
PINA1 = PinPin.PINA1
PINA2 = PinPin.PINA2
PINA3 = PinPin.PINA3
PINA4 = PinPin.PINA4
PINA5 = PinPin.PINA5
PINA6 = PinPin.PINA6
PINA7 = PinPin.PINA7