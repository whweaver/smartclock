# Main application for SmartClock processing

import env

import time
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

    def refresh_alarms(self):
        self.alarm_manager.refresh()

    def process(self):
        start_time = datetime.datetime.now()
        self.clock.process()
        self.alarm_manager.process()
        end_time = datetime.datetime.now()
        elapsed_time = end_time - start_time
        if elapsed_time < Application.CYCLE_TIME:
            time.sleep((Application.CYCLE_TIME - elapsed_time).total_seconds())

    def run(self):
        try:
            while True:
                self.process()
        except KeyboardInterrupt:
            print("Shutting down...")

if __name__ == '__main__':
    Application().run()
