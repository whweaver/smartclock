# Provides funtionality for processing the clock

import threading
import datetime
import pi_io

class Clock:
    def __init__(self):
        self.display = pi_io.Display()
        self.display.set_brightness(0.5)
        self.display.blink(pi_io.Display.BLINK_SOLID)
        self.hour = None
        self.minute = None
        super(Clock, self).__init__()

    def process(self):
        cur_time = datetime.datetime.now().time()
        if self.hour != cur_time.hour or self.minute != cur_time.minute:
            hour = cur_time.hour
            if hour > 12:
                hour -= 12
            self.display.update(hour, cur_time.minute)
            self.hour = hour
            self.minute = cur_time.minute
