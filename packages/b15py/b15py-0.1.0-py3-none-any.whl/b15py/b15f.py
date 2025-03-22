import serial
import os
import random
import time
import numpy as np
from ctypes import *
from typeguard import typechecked
from struct import pack, unpack

from utilities import *
from commands import Command
from ports import Port
from channels import Channel
from registers import DDRPin, PortPin, PinPin 

class B15F:
    def __init__(self, port: str):
        self.port = serial.Serial(port=port, baudrate=57600)
        info("Connection to B15F established!")

    def get_instance():
        try:
            return B15F(get_devices()[0])
        except:
            hint_error("Failed to find adapter for B15F!", "Is the USB connected properly?")

    def discard(self):
        try:
            self.port.reset_output_buffer()
            for i in range(0,16):
                self.port.write([Command.Discard])
                time.sleep(0.004)
                #self.delay_ms(4)
            self.port.reset_input_buffer()
        except:
            error("Discard failed!")


    def test_connection(self):
        dummy = int.from_bytes(os.urandom(1)) % 256

        self.port.write([Command.Test, dummy])

        response = list(self.port.read(size=2))

        if response[0] != OK:
            error("Testing connection failed! Bad OK value" + str(response[0]))
        elif response[1] != dummy:
            error("Testing connection failed! Bad response: " + str(response[1]))

    def get_board_info(self) -> list[str]:
        buffer = []
        self.port.write([Command.Info])

        n = int.from_bytes(self.port.read(), "big")

        print(n)

        while n > 0:
            len = int.from_bytes(self.port.read(), "big")
            string = self.port.read(size = len)

            buffer.append(string.decode("utf-8")[:len-1])
            n -= 1

        response = int.from_bytes(self.port.read(), "big")

        if (response != OK):
            error("Board information faulty! Code: " + str(response))

        return buffer

    def test_int_conv(self):
        random.seed(time.time())
        dummy = random.randint(0, 0xFFFF // 3)

        self.port.write([Command.IntTest, dummy & 0xFF, (dummy >> 8) & 0xFF])

        response = int.from_bytes(bytes(list(self.port.read(size=2))[::-1]))
        
        if response != dummy * 3:
            error("Bad int conv value: " + str(response))

    @typechecked
    def delay_ms(self, ms: int):
        if ms not in range(0,65535):
            error(f"Given value is not in range of a uint16_t (0..65535): " + ms)

        time.sleep(ms/1000)

    @typechecked
    def delay_us(self, us: int):
        if us not in range(0,65535):
            error(f"Given value is not in range of a uint16_t (0..65535): " + us)
        time.sleep(us/1000000)

    def activate_selftest_mode(self):
        self.port.write([Command.SelfTest])
        response = int.from_bytes(self.port.read())

        if response != OK:
            error("Self test failed!")

    @typechecked
    def digital_write(self, port: Port, value: int):
        command = Command.DigitalWrite0 if port == Port.Port0 else Command.DigitalWrite1
        if value not in range(0,256):
            error(f"Given value is not in range of a uint8_t (0..=255): {value}")

        self.port.write([command, reverse(value)])

        response = int.from_bytes(self.port.read())

        if response != OK:
            error("Bad value")

    @typechecked
    def digital_read(self, port: Port) -> int:
        command = Command.DigitalRead0 if port == Port.Port0 else Command.DigitalRead1
        self.port.reset_input_buffer()

        self.port.write([command])

        response = list(self.port.read())
        return reverse(response[0])

    @typechecked
    def analog_write(self, port: Port, value: int):
        command = Command.AnalogWrite0 if port == Port.Port0 else Command.AnalogWrite1
        if value not in range(0,65535):
            error(f"Given value is not in range of a uin16_t (0..65535): {value}")

        self.port.write([command, value & 0xFF, value >> 8])

        response = self.port.read()
        if list(response)[0] != OK:
            print(f"Analog write to port {port} failed!")

    @typechecked
    def analog_read(self, channel: Channel) -> int:
        self.port.reset_input_buffer()
        self.port.write([Command.AnalogRead, channel])

        response = list(self.port.read())

        if response[0] > 1023:
            error(f"Bad analog read response: " + response[0])

        return response[0]
    
    def read_dip_switch(self) -> int:
        self.port.reset_input_buffer()

        self.port.write([Command.ReadDipSwitch])

        response = int.from_bytes(self.port.read())
        return reverse(response)
    
    @typechecked
    def set_register(self, address: DDRPin | PortPin, value: int):
        self.set_mem8(address, value)

    @typechecked
    def get_register(self, address: PinPin) -> int:
        return self.get_mem8(address)

    @typechecked
    def set_mem8(self, address: int, value: int):
        if value not in range(0,256):
            error(f"Given value is not in range of a uin8_t (0..=255): {value}")

        self.port.reset_input_buffer()

        self.port.write([Command.SetMem8, address & 0xFF, address >> 8, value])

        response = int.from_bytes(self.port.read())

        if response != value:
            error("Bad set mem8 response: " + response)

    @typechecked
    def get_mem8(self, address: int) -> int:
        self.port.reset_input_buffer()

        self.port.write([Command.GetMem8, address & 0xFF, address >> 8])

        return int.from_bytes(self.port.read())


    @typechecked
    def set_mem16(self, address: int, value: int):
        if value not in range(0,65536):
            error(f"Given value is not in range of a uint16_t (0..=65535): {value}")
        
        self.port.reset_input_buffer()

        self.port.write([
            Command.SetMem16,
            address & 0xFF,
            address >> 8,
            value & 0xFF,
            value >> 8
        ])

        response = int.from_bytes(bytes(list(self.port.read(size=2))[::-1]))

        if response != value:
            error("Bad set mem16 response: " + response)


    @typechecked
    def set_pwm_value(self, value: int):
        self.port.reset_input_buffer()

        self.port.write([Command.PwmSetValue, value])

        response = int.from_bytes(self.port.read())

        if response != OK:
            error("Bad set pwm response: " + response)

    @typechecked
    def set_pwm_frequency(self, frequency: int) -> int:
        if frequency not in range(0,4294967296):
            error(f"Given frequency is not in range of a uint32_t (0..=4294967295): "+ frequency)
        self.port.reset_input_buffer()

        self.port.write([
            Command.PwmSetFreq,
            (frequency >> 0) & 0xFF,
            (frequency >> 8) & 0xFF,
            (frequency >> 16) & 0xFF,
            (frequency >> 24) & 0xFF
        ])

        return int.from_bytes(self.port.read())

    def get_interrupt_counter_offset(self) -> int:
        self.port.reset_input_buffer()

        self.port.write([Command.CounterOffset])

        return int.from_bytes(self.port.read())

    def set_servo_enabled(self):
        self.port.reset_input_buffer()

        self.port.write([Command.ServoEnable])

        response = int.from_bytes(self.port.read())

        if response != OK:
            error("Bad servo enable response: " + response)

    def set_servo_disabled(self):
        self.port.reset_input_buffer()

        self.port.write([Command.ServoDisable])

        response = int.from_bytes(self.port.read())

        if response != OK:
            error("Bad servo disable response: "+ response)

    @typechecked
    def set_servo_position(self, position: int):
        if position not in range(0,19001):
            error(f"Impulse length not in range (0..=19000): {position}")

        self.port.reset_input_buffer()

        self.port.write([
            Command.ServoSetPos,
            position & 0xFF,
            position >> 8
        ])

        response = int.from_bytes(self.port.read())

        if response != OK:
            error("Bad servo position response: " + response)
