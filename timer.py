"""
    TIMER.PY

    This file is used for creating a timer class,
    which will call a given function if enough time
    has elapsed. Used for sending the Router's
    periodic updates.
"""

import time
import random

class Timer:
    
    def __init__(self, period, callback_func):
        # Establish how regularly the callback function should be called.
        self.period = period
        self.callback_func = callback_func
        self.started = False


    def start_timer(self):
        """
            Figures out when the callback function should first be sent.
        """
        current_time = time.time()
        self.update_time = current_time + self.period
        self.next_trigger_allowed = current_time
        self.started = True

    
    def update_timer(self):
        """
            Calls the callback function if enough time has elapsed, and
            figures out when it should next be called.
        """
        if self.started is True:
            current_time = time.time()
            if current_time >= self.update_time:
                # The next periodic update is sent after the given time period,
                # +/- 20% to prevent excessive congestion due to periodic updates.
                random_offset = random.uniform(0.8, 1.2)
                self.update_time = current_time + (self.period * random_offset)
                self.callback_func()


    def triggered_update_allowed(self):
        """
            Measures whether enough time has passed since the last triggered
            update was sent out, ensuring that triggered updates don't take
            up too much bandwidth.
        """
        if self.started is True:
            current_time = time.time()
            if current_time >= self.next_trigger_allowed:
                # The next triggered update is allowed to be sent sometime between 1s
                # and 5s after the last one at the soonest.
                self.next_trigger_allowed = current_time + random.uniform(1.0,5.0)
                return True
            else:
                return False
