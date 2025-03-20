# Describe
A Python package to control the L9110 motor driver over I2C using smbus2.

# Installation
1. Create virtual environment: `python3 -m venv your_env`
2. Activate virtual environment: `source your_env/bin/activate`
3. install package: `pip install MKE-M17`

> **⚠️ Warning**  
> - Check hardware connection: Ensure your device is correctly connected to the I2C bus (SDA, SCL, VCC, GND) before using the package.  
> - Verify I2C address: Use the command `i2cdetect -y 1` on a Raspberry Pi to check the I2C address of the L9110 device.  
> - Resource management: The package supports context manager (`with` statement) to automatically close the I2C bus after use, preventing resource leaks. It is recommended to use this syntax whenever possible.

# How to use `MKE_M17` lib

## 1. Initialize the Driver
> Create an L9110 instance to control your device.

**Parameters:**

* `i2c_address` (int): The I2C address of the L9110 chip. Default is `0x40`.
* `i2c_bus_number` (int): The number of the I2C bus to use. Default is `1`.

**Example:**
> **⚠️ Warning:** Run in virtual environment (your_env/bin/python3.11)

```python
from MKE_M17 import L9110

# Default settings
l9110 = L9110()

# Custom address and bus
l9110 = L9110(address=0x42, bus_number=1)

# With context manager (recommended)
with L9110(address=0x42) as l9110:
    pass
```
## 2. Control Servos
> Use `control_servo()` to set servo angles.

**Args:**

* `servo_id` (int): 1 (S1) or 2 (S2).
* `degree` (int): Angle in degrees (default: 0-180).

**Returns:**
> `True` on success, `False` on failure.

**Example:**
```python
l9110.control_servo(1, 150)  # Servo 1 to 150°
l9110.control_servo(2, 90)   # Servo 2 to 90°
```

## 3. Control DC Motors
> Use `control_motor()` to set motor speed and direction.

**Args:**

* `motor_id` (int): 0 (MA) or 1 (MB).
* `percent` (float): Speed (0-100).
* `direction` (int): 0 (CW) or 1 (CCW).

**Returns:**
> `True` on success, `False` on failure.

**Example:** 
```python
l9110.control_motor(0, 50, 0)  # Motor A, 50%, clockwise
l9110.control_motor(1, 70, 1)  # Motor B, 70%, counterclockwise
```

## 4. Change I2C Address
> Update the device’s I2C address with `set_address()`.

**Args:**
* `new_address` (byte): New address (0x40-0x44).

**Returns:**
> `True` on success, `False` on failure.

**Example:**
```python
l9110.set_address(0x42)
# Output: "Set address successful. New address: 0x42"
```

## 5. Customize Servo Range
### Set new range degree.
> using `set_range_degree(min_degree, max_degree)` to set new range degree for servo motor

**Args:**
* `min_degree`(int): (0-359).
* `max_degree`(int): (1-360).

**Example:**
```python
l9110.set_range_degree(0, 270)
```
### Set new range pulse.
> using `set_range_pulse(min_pulse, max_pulse)` to set new range degree for servo motor

**Args:**
* `min_pulse`(int): (0-2814).
* `max_pulse`(int): (1-2815).

**Example:**
```python
l9110.set_range_pulse(600, 2400)
```