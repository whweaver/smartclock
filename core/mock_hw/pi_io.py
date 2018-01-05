# Provides interface to physical IO

import threading
import subprocess
import datetime

import alsaaudio

SUNRISE_WARM_PWM_PIN = 0
SUNRISE_COOL_PWM_PIN = 0

class PigpioDaemon:
    def __init__(self):
        print("Starting pigpio daemon")

    def __del__(self):
        print("Terminating pigpio daemon")

class SnoozeButton:
    GPIO_INPUTS = []
    GPIO_DEBOUNCE_COUNT = 5
    GPIO_SAMPLE_TIME = 0.010
    OFF_HOLD_TIME = datetime.timedelta(seconds=3)

    def __init__(self, alarm):
        self.ct = 0
        print("Initializing snooze button")

    def process(self):
        self.ct += 1
        if self.ct % 3000 == 0:
            self.alarm.reset()
        elif self.ct % 1000 == 0:
            self.alarm.snooze()

class Sunrise:
    def __init__(self):
        print("Initializing sunrise")

    def set_warm_brightness(self, brightness):
        print("Setting warm brightness to " + str(brightness))

    def set_cool_brightness(self, brightness):
        print("Setting cool brightness to " + str(brightness))

class Display:
    BLINK_ON_OFF_BIT = 0x01
    BLINK_OFF = 0x00
    BLINK_SOLID = 0x00 | BLINK_ON_OFF_BIT
    BLINK_2HZ = 0x02 | BLINK_ON_OFF_BIT
    BLINK_1HZ = 0x04 | BLINK_ON_OFF_BIT
    BLINK_0_5HZ = 0x06 | BLINK_ON_OFF_BIT

    def __init__(self):
        print("Initializing display")
        self.blink(self.BLINK_OFF)
        self.set_brightness(0)

    def __del__(self):
        print("Terminating display")

    def blink(self, blink):
        print("Blinking at " + str(blink))

    def set_brightness(self, brightness):
        if brightness > 1 or brightness < 0:
            raise PiIOException("Brightness must be between 0 and 1")
        print("Setting brightness to " + str(brightness))

    def update(self, hour, minute):
        print("Updating to %d:%0d".format(hour, minute))

class Speaker:
    MAX_VOLUME = 100
    VOLUME_INCREMENT = 1 / MAX_VOLUME

    def __init__(self):
        self.mixer = alsaaudio.Mixer()

    def set_volume(self, vol):
        if vol > 1 or vol < 0:
            raise PiIOException("Volume must be between 0 and 1")
        self.mixer.setvolume(vol * MAX_VOLUME)

class PiIOException(Exception):
    pass
