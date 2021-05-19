from machine import Pin, PWM
from time import sleep
import ulogging

'''
Pins 34-39 VP(36), VN(39) are input only (6pins), and also do not have internal pull-up resistors. But can be used for ADC
Pins 6, 7, 8, 11, 16, and 17 are used for connecting the embedded flash, and are not recommended for other uses
Pins high at boot GPIO 1,3,5,6-11,14,15
Reboot - (EN) is the 3.3V enable pin. Connect to ground to restart
Pin2 is connected to internal led
'''

ulogging.basicConfig(level=10) # Change logger global settings
logger = ulogging.getLogger(__name__)

testpin = 13
#PIN OUT TESTING
testout = Pin(testpin, Pin.OUT)
for _ in range(3):
    testout.value(0)
    logger.debug("{0} low".format(testpin))
    sleep(1)
    testout.value(1)
    logger.debug("{0} high".format(testpin))
    sleep(1)
'''
#PIN IN TESTING
button = Pin(4, Pin.IN, Pin.PULL_UP)

led1.value(0)
led2.value(0)

maxp = 2

while True:
    led1.value(button.value())
    led2.value(not led2.value())
    print("led1 ", led1.value(), " led2 ", led2.value(), maxp)
    sleep(0.1)

frequency = 5000
led = PWM(Pin(5), frequency)
            # frequency from 0 to 78125.
            # 5000Hz can be used for LED brightness
            # duty cycle from 0 to 1023 (100%) duty cycle

while True:
    for duty_cycle in range(0, 1024):
        led.duty(duty_cycle)
        print(duty_cycle, 0, 1100)
        sleep(0.005)

'''