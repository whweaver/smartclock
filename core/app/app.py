# Main application for SmartClock processing

import env

import time
import signal
import datetime

import clock
import alarm_manager
import pi_io

class Application:
    CYCLE_TIME = datetime.timedelta(milliseconds=10)

    def __init__(self):
        self.io_daemon = pi_io.PigpioDaemon()
        self.clock = clock.Clock()
        self.alarm_manager = alarm_manager.AlarmManager()
        signal.signal(signal.SIGINT, self.sig_handler)
        signal.signal(signal.SIGTERM, self.sig_handler)

    def process(self):
        start_time = datetime.datetime.now()
        self.clock.process()
        self.alarm_manager.process()
        self.io.process()
        end_time = datetime.datetime.now()
        time.sleep((CYCLE_TIME - (end_time - start_time)).total_seconds())

    def run(self):
        try:
            while True:
                self.process()
        except KeyboardInterrupt:
            print("Shutting down...")
