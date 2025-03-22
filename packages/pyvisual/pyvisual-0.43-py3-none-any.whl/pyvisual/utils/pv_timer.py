from kivy.clock import Clock


class PvTimer:
    def __init__(self):
        """Initialize the PvTimer."""
        self.start_time = None
        self.elapsed_time = 0
        self.is_running = False

    def start(self):
        """Start the timer."""
        if not self.is_running:
            self.start_time = Clock.get_time() - self.elapsed_time
            self.is_running = True

    def stop(self):
        """Stop the timer."""
        if self.is_running:
            self.elapsed_time = Clock.get_time() - self.start_time
            self.is_running = False

    def reset(self):
        """Reset the timer."""
        self.start_time = None
        self.elapsed_time = 0
        self.is_running = False

    def get_time(self):
        """Get the elapsed time in seconds."""
        if self.is_running:
            self.elapsed_time = Clock.get_time() - self.start_time
        return self.elapsed_time

    @staticmethod
    def schedule_function(callback, interval):
        """Schedule a function to be called at specified intervals.

        Args:
            callback (callable): The function to be scheduled.
            interval (float): The interval in seconds.
        """
        Clock.schedule_interval(callback, interval)

    @staticmethod
    def schedule_once(callback, delay=0):
        """Schedule a function to be called once after a delay.

        Args:
            callback (callable): The function to be scheduled.
            delay (float): The delay in seconds.
        """
        Clock.schedule_once(callback, delay)


if __name__ == "__main__":
    import time

    def scheduled_callback(dt):
        print(f"Scheduled function called at {dt:.2f} seconds interval.")

    def schedule_once_callback(dt):
        print(f"Scheduled once function called after {dt:.2f} seconds delay.")

    # Example usage of PvTimer for scheduling
    PvTimer.schedule_function(scheduled_callback, 1 / 2)  # Call function every 0.5 seconds
    PvTimer.schedule_once(schedule_once_callback, 3)  # Call function once after 3 seconds

    # Example usage of PvTimer for timing
    timer = PvTimer()
    timer.start()
    time.sleep(2)
    print(f"Elapsed time after 2 seconds: {timer.get_time():.2f} seconds")

    timer.stop()
    time.sleep(1)
    print(f"Elapsed time after stopping for 1 second: {timer.get_time():.2f} seconds")

    timer.start()
    time.sleep(1)
    print(f"Elapsed time after restarting for 1 second: {timer.get_time():.2f} seconds")

    timer.reset()
    print(f"Elapsed time after reset: {timer.get_time():.2f} seconds")
