#!/usr/bin/python3

from smbus2 import SMBus
import struct
import time

import SM16uout.SM16uout_data as data
I2C_MEM = data.I2C_MEM
CHANNEL_NO = data.CHANNEL_NO
CALIB = data.CALIB

class SM16uout: 
    """Python class to control the Sixteen 0-10V Analog Outputs

    Args:
        stack (int): Stack level/device number.
        i2c (int): i2c bus number
    """
    def __init__(self, stack=0, i2c=1):
        if stack < 0 or stack > data.STACK_LEVEL_MAX:
            raise ValueError("Invalid stack level!")
        self._hw_address_ = data.SLAVE_OWN_ADDRESS_BASE + stack
        self._i2c_bus_no = i2c
        self.bus = SMBus(self._i2c_bus_no)
        try:
            self.bus.read_byte_data(self._hw_address_, I2C_MEM.REVISION_HW_MAJOR_ADD)
            time.sleep(0.01)
        except Exception:
            print("{} not detected!".format(data.CARD_NAME))
            raise

    def _get_byte(self, address):
        return self.bus.read_byte_data(self._hw_address_, address)
    def _get_word(self, address):
        return self.bus.read_word_data(self._hw_address_, address)
    def _get_i16(self, address):
        buf = self.bus.read_i2c_block_data(self._hw_address_, address, 2)
        i16_value = struct.unpack("h", bytearray(buf))[0]
        return i16_value
    def _get_float(self, address):
        buf = self.bus.read_i2c_block_data(self._hw_address_, address, 4)
        float_value = struct.unpack("f", bytearray(buf))[0]
        return float_value
    def _get_i32(self, address):
        buf = self.bus.read_i2c_block_data(self._hw_address_, address, 4)
        i32_value = struct.unpack("i", bytearray(buf))[0]
        return i32_value
    def _get_u32(self, address):
        buf = self.bus.read_i2c_block_data(self._hw_address_, address, 4)
        u32_value = struct.unpack("I", bytearray(buf))[0]
        return u32_value
    def _get_block_data(self, address, byteno=4):
        return self.bus.read_i2c_block_data(self._hw_address_, address, byteno)

    def _set_byte(self, address, value):
        self.bus.write_byte_data(self._hw_address_, address, int(value))
    def _set_word(self, address, value):
        self.bus.write_word_data(self._hw_address_, address, int(value))
    def _set_float(self, address, value):
        ba = bytearray(struct.pack("f", value))
        self.bus.write_block_data(self._hw_address_, address, ba)
    def _set_i32(self, address, value):
        ba = bytearray(struct.pack("i", value))
        self.bus.write_block_data(self._hw_address_, address, ba)
    def _set_block(self, address, ba):
        self.bus.write_i2c_block_data(self._hw_address_, address, ba)

    @staticmethod
    def _check_channel(channel_type, channel):
        if not (0 <= channel and channel <= CHANNEL_NO[channel_type]):
            raise ValueError("Invalid {} channel number. Must be [1..{}]!".format(channel_type, CHANNEL_NO[channel_type]))
    def _calib_set(self, channel, value):
        ba = bytearray(struct.pack("f", value))
        ba.extend([channel, data.CALIBRATION_KEY])
        self._set_block(I2C_MEM.CALIB_VALUE, ba)

    def _calib_reset(self, channel):
        ba = bytearray([channel, data.CALIBRATION_KEY])
        self._set_block(I2C_MEM.CALIB_CHANNEL, ba)

    def calib_status(self):
        """Get current calibration status of device.

        Returns:
            (int) Calib status
        """
        status = self._get_byte(I2C_MEM.CALIB_STATUS)
        return status

    def get_version(self):
        """Get firmware version.

        Returns: (int) Firmware version number
        """
        version_major = self._get_byte(I2C_MEM.REVISION_MAJOR_ADD)
        time.sleep(0.01)
        version_minor = self._get_byte(I2C_MEM.REVISION_MINOR_ADD)
        version = str(version_major) + "." + str(version_minor)
        return version

    def get_u_out(self, channel):
        """Get 0-10V output channel value in volts.

        Args:
            channel (int): Channel number

        Returns:
            (float) 0-10V output value
        """
        self._check_channel("u_out", channel)
        value = self._get_word(I2C_MEM.U_OUT + (channel - 1) * 2)
        return value / data.VOLT_TO_MILIVOLT

    def set_u_out(self, channel, value):
        """Set 0-10V output channel value in volts.

        Args:
            channel (int): Channel number
            value (float): Voltage value
        """
        self._check_channel("u_out", channel)
        value = value * data.VOLT_TO_MILIVOLT
        self._set_word(I2C_MEM.U_OUT + (channel - 1) * 2, value)

    def cal_u_out(self, channel, value):
        """Calibrate 0-10V output channel.
        Calibration must be done in 2 points at min 5V apart.

        Args:
            channel (int): Channel number
            value (float): Real(measured) voltage value
        """
        self._check_channel("u_out", channel)
        self._calib_set(CALIB.U_OUT_CH1 + channel, value)

    def get_led(self, led):
        """Get led state.

        Args:
            led (int): Led number

        Returns:
            0(OFF) or 1(ON)
        """
        self._check_channel("led", led)
        val = self._get_byte(I2C_MEM.LEDS)
        if (val & (1 << (led - 1))) != 0:
            return 1
        return 0
    def get_all_leds(self):
        """Get all leds state as bitmask.

        Returns:
            (int) Leds state bitmask
        """
        return self._get_word(I2C_MEM.LEDS)
    def set_led(self, led, val):
        """Set led state.

        Args:
            led (int): Led number
            val: 0(OFF) or 1(ON)
        """
        self._check_channel("led", led)
        if val != 0:
            self._set_byte(I2C_MEM.LED_SET, led)
        else:
            self._set_byte(I2C_MEM.LED_CLR, led)
    def set_all_leds(self, val):
        """Set all leds states as bitmask.

        Args:
            val (int): Led bitmask
        """
        if(not (0 <= val and val <= (1 << CHANNEL_NO["led"]) - 1)):
            raise ValueError("Invalid led mask!")
        self._set_word(I2C_MEM.LEDS, val)

    def get_rs485(self):
        """NOT IMPLEMENTED"""
        # TODO: Implement
        raise NotImplementedError

    def set_rs485(self, modbus, modbusId, baudrate = 38400, stopbits = 1, parity = 0):
        """Set the RS485 port parameters

        Args:
            modbus (0/1): 1: turn ON, 2: turn OFF
            modbusId (1..254): modbus ID
            baudrate (1200..115200): baud rate (default: 38400)
            stopbits (1/2): stop bits (default: 1)
            parity (0/1/2): stop bits (default: 0 - None)
        """
        settings = (
                (baudrate & 0xFFFFFF) |
                ((modbus & 0xF) << 24) |
                ((parity & 0x3) << 28) |
                ((stopbits & 0x3) << 30)
        )
        data_bytes = settings.to_bytes(4, byteorder='little')
        data_bytes += modbusId.to_bytes(1, byteorder='little')
        self._set_block(I2C_MEM.MODBUS_ID_OFFSET_ADD, data_bytes)

    def disable_rs485(self):
        """Disable modbus and free the RS485 for Raspberry usage"""
        self.set_rs485(0, 1)

    def wdt_reload(self):
        """Reload watchdog."""
        self._set_byte(I2C_MEM.WDT_RESET_ADD, data.WDT_RESET_SIGNATURE)
    def wdt_get_period(self):
        """Get watchdog period in seconds.

        Returns:
            (int) Watchdog period in seconds
        """
        return self._get_word(I2C_MEM.WDT_INTERVAL_GET_ADD)
    def wdt_set_period(self, period):
        """Set watchdog period.

        Args:
            period (int): Channel number
        """
        return self._set_word(I2C_MEM.WDT_INTERVAL_SET_ADD, period)
    def wdt_get_init_period(self):
        """Get watchdog initial period.

        Returns:
            (int) Initial watchdog period in seconds
        """
        return self._get_word(I2C_MEM.WDT_INIT_INTERVAL_GET_ADD)
    def wdt_set_init_period(self, period):
        """Set watchdog initial period.

        Args:
            period (int): Initial period in second
        """
        return self._set_word(I2C_MEM.WDT_INIT_INTERVAL_SET_ADD, period)

    def wdt_get_off_period(self):
        """Get watchdog off period in seconds.

        Returns:
            (int) Watchfog off period in seconds.
        """
        return self._get_i32(I2C_MEM.WDT_POWER_OFF_INTERVAL_GET_ADD)
    def wdt_set_off_period(self, period):
        """Set off period in seconds

        Args:
            period (int): Off period in seconds
        """
        return self._set_i32(I2C_MEM.WDT_POWER_OFF_INTERVAL_SET_ADD, period)
    def wdt_get_reset_count(self):
        """Get watchdog reset count.

        Returns:
            (int) Watchdog reset count
        """
        return self._get_word(I2C_MEM.WDT_RESET_COUNT_ADD)
    def wdt_clear_reset_count(self):
        """Clear watchdog counter. """
        return self._set_i32(I2C_MEM.WDT_CLEAR_RESET_COUNT_ADD, data.WDT_RESET_COUNT_SIGNATURE)

    def get_button(self):
        """Get button status.

        Returns:
            (bool) status
                True(ON)/False(OFF)
        """
        state = self._get_byte(I2C_MEM.BUTTON)
        if(state & 1):
            return True
        else:
            return False
    def get_button_latch(self):
        """Get button latch status.

        Returns:
            (bool) status
                True(ON)/False(OFF)
        """
        state = self._get_byte(I2C_MEM.BUTTON)
        if(state & 2):
            state &= ~2
            self._set_byte(I2C_MEM.BUTTON, state)
            return True
        else:
            return False
