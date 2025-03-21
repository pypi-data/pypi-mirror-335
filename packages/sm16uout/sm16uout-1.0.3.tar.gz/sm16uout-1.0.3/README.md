# Welcome to SM16uout’s documentation!

# Install

```bash
sudo pip install SM16uout
```

or

```bash
sudo pip3 install SM16uout
```

# Update

```bash
sudo pip install SM16uout -U
```

or

```bash
sudo pip3 install SM16uout -U
```

# Initiate class

```console
$ python
Python 3.11.8 (main, Feb 12 2024, 14:50:05) [GCC 13.2.1 20230801] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import SM16uout.SM16uout as m
>>> SM16uout = m()
>>>
```

# Documentation

<a id="module-SM16uout"></a>

### *class* SM16uout.SM16uout(stack=0, i2c=1)

Bases: `object`

Python class to control the Sixteen 0-10V Analog Outputs

* **Parameters:**
  * **stack** (*int*) – Stack level/device number.
  * **i2c** (*int*) – i2c bus number

#### calib_status()

Get current calibration status of device.

* **Returns:**
  (int) Calib status

#### get_version()

Get firmware version.

Returns: (int) Firmware version number

#### get_u_out(channel)

Get 0-10V output channel value in volts.

* **Parameters:**
  **channel** (*int*) – Channel number
* **Returns:**
  (float) 0-10V output value

#### set_u_out(channel, value)

Set 0-10V output channel value in volts.

* **Parameters:**
  * **channel** (*int*) – Channel number
  * **value** (*float*) – Voltage value

#### cal_u_out(channel, value)

Calibrate 0-10V output channel.
Calibration must be done in 2 points at min 5V apart.

* **Parameters:**
  * **channel** (*int*) – Channel number
  * **value** (*float*) – Real(measured) voltage value

#### get_led(led)

Get led state.

* **Parameters:**
  **led** (*int*) – Led number
* **Returns:**
  0(OFF) or 1(ON)

#### get_all_leds()

Get all leds state as bitmask.

* **Returns:**
  (int) Leds state bitmask

#### set_led(led, val)

Set led state.

* **Parameters:**
  * **led** (*int*) – Led number
  * **val** – 0(OFF) or 1(ON)

#### set_all_leds(val)

Set all leds states as bitmask.

* **Parameters:**
  **val** (*int*) – Led bitmask

#### get_rs485()

NOT IMPLEMENTED

#### set_rs485(modbus, modbusId, baudrate=38400, stopbits=1, parity=0)

Set the RS485 port parameters

* **Parameters:**
  * **modbus** (*0/1*) – 1: turn ON, 2: turn OFF
  * **modbusId** (*1..254*) – modbus ID
  * **baudrate** (*1200..115200*) – baud rate (default: 38400)
  * **stopbits** (*1/2*) – stop bits (default: 1)
  * **parity** (*0/1/2*) – stop bits (default: 0 - None)

#### disable_rs485()

Disable modbus and free the RS485 for Raspberry usage

#### wdt_reload()

Reload watchdog.

#### wdt_get_period()

Get watchdog period in seconds.

* **Returns:**
  (int) Watchdog period in seconds

#### wdt_set_period(period)

Set watchdog period.

* **Parameters:**
  **period** (*int*) – Channel number

#### wdt_get_init_period()

Get watchdog initial period.

* **Returns:**
  (int) Initial watchdog period in seconds

#### wdt_set_init_period(period)

Set watchdog initial period.

* **Parameters:**
  **period** (*int*) – Initial period in second

#### wdt_get_off_period()

Get watchdog off period in seconds.

* **Returns:**
  (int) Watchfog off period in seconds.

#### wdt_set_off_period(period)

Set off period in seconds

* **Parameters:**
  **period** (*int*) – Off period in seconds

#### wdt_get_reset_count()

Get watchdog reset count.

* **Returns:**
  (int) Watchdog reset count

#### wdt_clear_reset_count()

Clear watchdog counter.

#### get_button()

Get button status.

* **Returns:**
  (bool) status
  : True(ON)/False(OFF)

#### get_button_latch()

Get button latch status.

* **Returns:**
  (bool) status
  : True(ON)/False(OFF)

<!-- vi:se ts=4 sw=4 et: -->
