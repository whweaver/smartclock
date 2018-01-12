# Provides interface to physical IO

import threading
import subprocess
import datetime

import alsaaudio
import pigpio

SUNRISE_WARM_PWM_PIN = 0
SUNRISE_COOL_PWM_PIN = 0

class PigpioDaemon:
    def __init__(self):
        updatable_gpio = (1 << SUNRISE_WARM_PWM_PIN) + (1 << SUNRISE_COOL_PWM_PIN)
        self.daemon_process = subprocess.Popen(["sudo", "pigpiod", "-s", "10", "-x", str(updatable_gpio)])

    def __del__(self):
        self.daemon_process.terminate()

class SnoozeButton:
    GPIO_INPUTS = []
    GPIO_DEBOUNCE_COUNT = 5
    GPIO_SAMPLE_TIME = 0.010
    OFF_HOLD_TIME = datetime.timedelta(seconds=3)

    def __init__(self, alarm):
        self.pressed = False
        self.alarm = alarm
        self.debounce_counts = [0] * len(GPIO_INPUTS)
        self.last_change_time = datetime.datetime.now()
        self.pi = pigpio.pi()

    def __del__(self):
        self.pi.stop()

    def process(self):
        gpio_levels = self._get_gpio_levels()
        self._adjust_counts(gpio_levels)
        self._update_pressed_state()
        self._update_off_state()

    def _get_gpio_levels(self):
        levels = []
        for gpio in GPIO_INPUTS:
            levels.append(self.pi.read(gpio))
        return levels

    def _adjust_counts(self, levels):
        for idx, level in enumerate(levels):
            if level != 0 and self.debounce_counts[idx] < GPIO_DEBOUNCE_COUNT:
                self.debounce_counts[idx] += 1
            elif level == 0 and self.debounce_counts[idx] > 0:
                self.debounce_counts[idx] -= 1

    def _update_pressed_state(self):
        pressed_ct = 0
        unpressed_ct = 0
        for count in self.debounce_counts:
            if count >= GPIO_DEBOUNCE_COUNT:
                pressed_ct += 1
            elif count <= 0:
                unpressed_ct += 1

        new_pressed = None
        if pressed_ct > 0:
            new_pressed = True
        elif unpressed_ct == len(self.debounce_counts):
            new_pressed = False

        if new_pressed != None:
            if not self.pressed and new_pressed:
                self.alarm.snooze()
                
            if self.pressed and not new_pressed:
                self.last_change_time = datetime.datetime.now()

            with self.state_lock:
                self.pressed = new_pressed

    def _update_off_state(self):
        if self.pressed and datetime.datetime.now() - self.last_change_time >= OFF_HOLD_TIME:
            self.alarm.reset()

class Sunrise:
    SUNRISE_PWM_FREQ = 20000
    HW_PWM_MAX_DUTY_CYCLE = 1000000

    def __init__(self):
        self.pi = pigpio.pi()

    def __del__(self):
        self.pi.stop()

    def set_warm_brightness(self, brightness):
        self._set_brightness(SUNRISE_WARM_PWM_PIN, brightness)

    def set_cool_brightness(self, brightness):
        self._set_brightness(SUNRISE_COOL_PWM_PIN, brightness)

    def _set_brightness(self, pin, brightness):
        if brightness > 1 or brightness < 0:
            raise PiIOException("Brightness must be between 0 and 1")

        self.pi.hardware_PWM(pin, SUNRISE_PWM_FREQ, brightness * HW_PWM_MAX_DUTY_CYCLE)

class Display:
    BLINK_ON_OFF_BIT = 0x01
    BLINK_OFF = 0x00
    BLINK_SOLID = 0x00 | BLINK_ON_OFF_BIT
    BLINK_2HZ = 0x02 | BLINK_ON_OFF_BIT
    BLINK_1HZ = 0x04 | BLINK_ON_OFF_BIT
    BLINK_0_5HZ = 0x06 | BLINK_ON_OFF_BIT

    BLINK_CMD = 0x80
    START_OSC_CMD = 0x21
    BRIGHTNESS_CMD = 0xE0
    I2C_BUS = 0
    I2C_ADDRESS = 0x70
    DIGIT_DATA_ADDR = 0x00
    HEX_TO_BACKPACK_CODE = [
        0x34, # 0
        0x06, # 1
        0x5B, # 2
        0x4F, # 3
        0x66, # 4
        0x6D, # 5
        0x7D, # 6
        0x07, # 7
        0x7F, # 8
        0x6F, # 9
        0x77, # A
        0x7C, # b
        0x39, # C
        0x5E, # d
        0x79, # E
        0x71  # F
    ]
    COLON_BACKPACK_CODE = 0x02

    def __init__(self):
        self.pi = pigpio.pi()
        self.i2c = self.pi.i2c_open(I2C_BUS, I2C_ADDRESS, 0)
        self.pi.i2c_write_byte(self.i2c, START_OSC_CMD) # Start oscillator
        self.blink(BLINK_OFF)
        self.set_brightness(0)

    def __del__(self):
        self.pi.i2c_close(self.i2c)
        self.pi.stop()

    def blink(self, blink):
        self.pi.i2c_write_byte(self.i2c, BLINK_CMD | blink)

    def set_brightness(self, brightness):
        if brightness > 1 or brightness < 0:
            raise PiIOException("Brightness must be between 0 and 1")
        scaled_br = int(round(brightness * 15))
        self.pi.i2c_write_byte(self.i2c, BRIGHTNESS_CMD | scaled_br)

    def update(self, hour, minute):
        buf = [
            0x00, HEX_TO_BACKPACK_CODE[hour // 10],
            0x00, HEX_TO_BACKPACK_CODE[hour % 10],
            0x00, COLON_BACKPACK_CODE,
            0x00, HEX_TO_BACKPACK_CODE[minute // 10],
            0x00, HEX_TO_BACKPACK_CODE[minute % 10]
        ]
        self.pi.i2c_write_i2c_block_data(self.i2c, DIGIT_DATA_ADDR, buf)

class Speaker:
    MAX_VOLUME = 100
    VOLUME_INCREMENT = 1 / MAX_VOLUME

    def __init__(self):
        self.mixer = alsaaudio.Mixer()

    def set_volume(self, vol):
        if vol > 1 or vol < 0:
            raise PiIOException("Volume must be between 0 and 1")
        self.mixer.setvolume(int(vol * Speaker.MAX_VOLUME))

class PiIOException(Exception):
    pass
