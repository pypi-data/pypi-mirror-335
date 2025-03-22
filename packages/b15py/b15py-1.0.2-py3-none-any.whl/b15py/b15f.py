import serial
import os
import random
import time
from typeguard import typechecked
import matplotlib.pyplot as plt

from .utilities import *
from .commands import Command
from .ports import Port
from .channels import Channel
from .registers import DDRPin, PortPin, PinPin 

class B15F:
    def __init__(self, port: str):
        self.__port = serial.Serial(port=port, baudrate=57600)
        info("Connection to B15F established!")

    def get_instance():
        try:
            return B15F(get_devices()[0])
        except:
            if len(get_devices()) == 0:
                hint_error("Failed to find adapter for B15F!", "Is the USB connected properly? (Connection left to right: RX TX GN)")
            
    def discard(self):
        try:
            self.__port.reset_output_buffer()
            for i in range(0,16):
                self.__port.write([Command.Discard])
                time.sleep(0.004)
                self.delay_ms(4)
            self.__port.reset_input_buffer()
        except:
            error("Discard failed!")


    def test_connection(self):
        dummy = int.from_bytes(os.urandom(1)) % 256

        self.__port.write([Command.Test, dummy])

        response = list(self.__port.read(size=2))

        if response[0] != OK:
            error("Testing connection failed! Bad OK value: " + str(response[0]))
        elif response[1] != dummy:
            error("Testing connection failed! Bad response value: " + str(response[1]))


    def get_board_info(self):
        buffer = []
        self.__port.write([Command.Info])

        n = int.from_bytes(self.__port.read(), "big")

        while n > 0:
            len = int.from_bytes(self.__port.read(), "big")
            string = self.__port.read(size = len)

            buffer.append(string.decode("utf-8")[:len-1])
            n -= 1

        response = int.from_bytes(self.__port.read(), "big")

        if (response != OK):
            error("Board information faulty! Faulty OK: " + str(response))

        info(f"AVR Firmware Version: {buffer[0]} um {buffer[1]} ({buffer[2]})")

    def test_int_conv(self):
        random.seed(time.time())
        dummy = random.randint(0, 0xFFFF // 3)

        self.__port.write([Command.IntTest, dummy & 0xFF, (dummy >> 8) & 0xFF])

        response = int.from_bytes(bytes(list(self.__port.read(size=2))[::-1]))
        
        if response != dummy * 3:
            error("Bad int conv value: " + str(response))

    """
    Sleeps for the given amount of millis (if its in the range of a uint16_t)
    """
    @typechecked
    def delay_ms(self, ms: int):
        if ms not in range(0,65535):
            error(f"Given value is not in range of a uint16_t (0..65535): " + ms)

        time.sleep(ms/1000)

    """
    Sleeps for the given amount of micros (if its in the range of a uint16_t)
    """
    @typechecked
    def delay_us(self, us: int):
        if us not in range(0,65536):
            error(f"Given value is not in range of a uint16_t (0..=65535): " + us)
        time.sleep(us/1000000)

    def activate_selftest_mode(self):
        self.__port.write([Command.SelfTest])
        response = int.from_bytes(self.__port.read())

        if response != OK:
            error("Self test failed!")

    """
    Writes the value (uint8_t) to the given digital port
    """
    @typechecked
    def digital_write(self, port: Port, value: int):
        command = Command.DigitalWrite0 if port == Port.Port0 else Command.DigitalWrite1
        if value not in range(0,256):
            error(f"Given value is not in range of a uint8_t (0..=255): {value}")

        self.__port.write([command, reverse(value)])

        response = int.from_bytes(self.__port.read())

        if response != OK:
            error("Did not receive the correct OK value on digital_write")

    """
    Reads the given digital port and returns the read value 
    """
    @typechecked
    def digital_read(self, port: Port) -> int:
        command = Command.DigitalRead0 if port == Port.Port0 else Command.DigitalRead1
        self.__port.reset_input_buffer()

        self.__port.write([command])

        response = list(self.__port.read())
        return reverse(response[0])

    """
    Writes the value (uint16_t) to the given analog port
    """
    @typechecked
    def analog_write(self, port: Port, value: int):
        self.__port.reset_input_buffer()
        command = Command.AnalogWrite0 if port == Port.Port0 else Command.AnalogWrite1
        if value not in range(0,1024):
            error(f"Given value is not in range (0..=1023): {value}")

        self.__port.write([command, value & 0xFF, value >> 8])

        response = int.from_bytes(bytes(list(self.__port.read())[::-1]))
        if response != OK:
            error(f"Analog write to port {port} failed!")


    """
    Reads the given analog channel and returns the read value
    """
    @typechecked
    def analog_read(self, channel: Channel) -> int:
        self.__port.reset_input_buffer()
        self.__port.write([Command.AnalogRead, channel])

        response = list(self.__port.read())

        if response[0] > 1023:
            error(f"Bad analog read response (exceeds 1023): " + response[0])

        return response[0]
    
    """
    Reads the dip switch states. The return is an 8 bit long integer, where each bit is the state of the dip switch
    """
    def read_dip_switch(self) -> int:
        self.__port.reset_input_buffer()

        self.__port.write([Command.ReadDipSwitch])

        response = int.from_bytes(self.__port.read())
        return reverse(response)
    
    """
    Sets a value to the given DDR or Port register
    """
    @typechecked
    def set_register(self, address: DDRPin | PortPin, value: int):
        self.set_mem8(address, value)

    """
    Retrieves the value from the given Pin register
    """
    @typechecked
    def get_register(self, address: PinPin) -> int:
        return self.get_mem8(address)

    """
    Sets a value of 8 bit at the given memory address
    """
    @typechecked
    def set_mem8(self, address: int, value: int):
        if value not in range(0,256):
            error(f"Given value is not in range of a uin8_t (0..=255): {value}")

        self.__port.reset_input_buffer()

        self.__port.write([Command.SetMem8, address & 0xFF, address >> 8, value])

        response = int.from_bytes(self.__port.read())

        if response != value:
            error("Bad set mem8 response: " + response)

    """
    Retrieves the value at the given memory address
    """
    @typechecked
    def get_mem8(self, address: int) -> int:
        self.__port.reset_input_buffer()

        self.__port.write([Command.GetMem8, address & 0xFF, address >> 8])

        return int.from_bytes(self.__port.read())

    """
    Sets a value of 16 bit length to the address in memory
    """
    @typechecked
    def set_mem16(self, address: int, value: int):
        if value not in range(0,65536):
            error(f"Given value is not in range of a uint16_t (0..=65535): {value}")
        
        self.__port.reset_input_buffer()

        self.__port.write([
            Command.SetMem16,
            address & 0xFF,
            address >> 8,
            value & 0xFF,
            value >> 8
        ])

        response = int.from_bytes(bytes(list(self.__port.read(size=2))[::-1]))

        if response != value:
            error("Bad set mem16 response: " + response)

    """
    Retrieves the 16 bit value at the given address
    """
    @typechecked
    def get_mem16(self, address: int) -> int:
        self.__port.reset_input_buffer()

        self.__port.write([Command.GetMem16, address & 0xFF, address >> 8])

        return int.from_bytes(self.__port.read())

    """
    Sets the value for the pulse width modulation signal
    """
    @typechecked
    def set_pwm_value(self, value: int):
        self.__port.reset_input_buffer()

        self.__port.write([Command.PwmSetValue, value])

        response = int.from_bytes(self.__port.read())

        if response != OK:
            error("Bad set pwm response: " + response)

    """
    Sets the frequency for the pulse width modulation signal
    """
    @typechecked
    def set_pwm_frequency(self, frequency: int) -> int:
        if frequency not in range(0,4294967296):
            error(f"Given frequency is not in range of a uint32_t (0..=4294967295): "+ frequency)
        self.__port.reset_input_buffer()

        self.__port.write([
            Command.PwmSetFreq,
            (frequency >> 0) & 0xFF,
            (frequency >> 8) & 0xFF,
            (frequency >> 16) & 0xFF,
            (frequency >> 24) & 0xFF
        ])

        return int.from_bytes(self.__port.read())

    """
    Retrieves the interrupt counter offset of the board
    """
    def get_interrupt_counter_offset(self) -> int:
        self.__port.reset_input_buffer()

        self.__port.write([Command.CounterOffset])

        return int.from_bytes(self.__port.read())

    """
    Enables the servo signal on the board
    """
    def set_servo_enabled(self):
        self.__port.reset_input_buffer()

        self.__port.write([Command.ServoEnable])

        response = int.from_bytes(self.__port.read())

        if response != OK:
            error("Bad servo enable response: " + response)

    """
    Disables the servo signal on the board
    """
    def set_servo_disabled(self):
        self.__port.reset_input_buffer()

        self.__port.write([Command.ServoDisable])

        response = int.from_bytes(self.__port.read())

        if response != OK:
            error("Bad servo disable response: "+ response)

    """
    Sets the position of the servo through the servo signal on the board
    """
    @typechecked
    def set_servo_position(self, position: int):
        if position not in range(0,19001):
            error(f"Impulse length not in range (0..=19000): {position}")

        self.__port.reset_input_buffer()

        self.__port.write([
            Command.ServoSetPos,
            position & 0xFF,
            position >> 8
        ])

        response = int.from_bytes(self.__port.read())

        if response != OK:
            error("Bad servo position response: " + response)

    ##########
    # EXTRAS #
    ##########

    @typechecked
    def general_plot(self, x_vals: list[int], y_vals: list[int], title: str, x_label: str, y_label: str, grid_visible: bool = False):
        plt.plot(x_vals, y_vals)
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.grid(grid_visible)
        plt.show()

    """
    Creates a plot from the values that are written and read of the given ports
    """
    @typechecked
    def digital_plot(self, port: Port, range: range, title: str, x_label: str, y_label: str, grid_visible: bool = False):
        x_vals = []
        y_vals = []
        for i in range:
            self.digital_write(port, i)
            x_vals.append(i)
            y_vals.append(self.digital_read(port))
        plt.plot(x_vals, y_vals)
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.grid(grid_visible)
        plt.show()

    """
    Creates a plot that will be updated while the code is running with the values that are written and read from the given ports
    """
    @typechecked
    def digital_plot_live(self, port: Port, range: range, title: str, x_label: str, y_label: str, grid_visible: bool = False):
        x_vals = []
        y_vals = []

        plt.ion()
        
        figure, ax = plt.subplots(figsize=(10, 8))
        line1, = ax.plot(x_vals, y_vals)
        ax.set_xlim(range.start, range.stop)
        ax.set_ylim(0,256)
        
        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.grid(grid_visible)

        for i in range:
            self.digital_write(port, i)
            x_vals.append(i)
            y_vals.append(self.digital_read(port))
            line1.set_xdata(x_vals)
            line1.set_ydata(y_vals)
            figure.canvas.draw()
            figure.canvas.flush_events()

        plt.ioff()
        plt.show()

    @typechecked
    def analog_plot(self, write_port: Port, read_channel: Channel, range: range, title: str, x_label: str, y_label: str, grid_visible: bool = False):
        x_vals = []
        y_vals = []
        for i in range:
            self.analog_write(write_port, i)
            x_vals.append(i)
            y_vals.append(self.analog_read(read_channel))
        plt.plot(x_vals, y_vals)
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.grid(grid_visible)
        plt.show()