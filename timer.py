import time

class Timer:
    def __init__(self, period, callback_func):
        self.period = period
        self.callback_func = callback_func
        self.started = False

    def start_timer(self):
        current_time = time.time()
        self.update_time = current_time + self.period
        self.started = True
    
    def update_timer(self):
        if self.started == True:
            current_time = time.time()
            if current_time >= self.update_time:
                self.update_time = current_time + self.period
                self.callback_func()
    
    def force_callback(self):
        if self.started == True:
            current_time = time.time()
            self.update_time = current_time + self.period
            self.callback_func()

