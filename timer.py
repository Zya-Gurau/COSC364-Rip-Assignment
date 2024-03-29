"""
    TIMER.PY

    This file is used for creating a timer class,
    which will call a given function if enough time
    has elapsed. Used for sending the Router's
    periodic updates.
"""

import time

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
        self.started = True

    
    def update_timer(self):
        """
            Calls the callback function if enough time has elapsed, and
            figures out when it should next be called.
        """
        if self.started == True:
            current_time = time.time()
            if current_time >= self.update_time:
                self.update_time = current_time + self.period
                self.callback_func()


    # DO WE NEED THIS FUNCTION FOR ANYTHING???? IT IS NEVER CALLED -----------------------------------------------------------------
    def force_callback(self):
        if self.started == True:
            current_time = time.time()
            self.update_time = current_time + self.period
            self.callback_func()
