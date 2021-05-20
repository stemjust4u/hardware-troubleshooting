import time, logging
import pigpio # http://abyz.co.uk/rpi/pigpio/python.html

class Encoder:

    def __init__(self, pi, gpio):

        self.pi = pi
        self.gpio = gpio
        self._watchdog = 200 # Milliseconds.
        self._high_tick = None
        self._period = None
        pi.set_mode(gpio, pigpio.INPUT)
        self._cb = pi.callback(gpio, pigpio.RISING_EDGE, self._cbf)
        pi.set_watchdog(gpio, self._watchdog)

    def _cbf(self, gpio, level, tick):   # gpio is pin with level change. level is rising/falling(or none), tick is time counter (usec)

        if level == 1: # Rising edge.
            if self._high_tick is not None:
                self._period = pigpio.tickDiff(self._high_tick, tick)
            self._high_tick = tick
        elif level == 2: # Watchdog timeout.
            if self._period is not None:
                if self._period < 2000000000:
                    self._period += (self._watchdog * 1000)

    def getdata(self):
        return self._period

    def cancel(self):
        """
        Cancels the Encoder and releases resources.
        """
        self.pi.set_watchdog(self.gpio, 0) # cancel watchdog
        self._cb.cancel()

if __name__ == "__main__":

    import time
    import pigpio

    gpioPin = 26
    RUN_TIME = 60.0
    SAMPLE_TIME = 1.0
    pi = pigpio.pi()
    encoder1 = Encoder(pi, gpioPin)
    start = time.time()
    while (time.time() - start) < RUN_TIME:
        time.sleep(SAMPLE_TIME)
        print("Period: {0} ms".format(encoder1.getdata()/1000))
    encoder1.cancel()
    pi.stop()