from machine import Pin, PWM, ADC
from time import sleep
from mytools import valmap
import ulogging, utime
from encoder import Encoder

'''
Pins 32-39 - ADC
Pins 34-39 are input only, and also do not have internal pull-up resistors. But can be used for ADC
 VP(36), VN(39) are input only
Pins 6, 7, 8, 11, 16, and 17 are used for connecting the embedded flash, and are not recommended for other uses
Pins high at boot GPIO 1,3,5,6-11,14,15
Reboot - (EN) is the 3.3V enable pin. Connect to ground to restart
Pin2 is connected to internal led (fails pull_up)
'''

ulogging.basicConfig(level=20) # Change logger global settings
logger = ulogging.getLogger(__name__)

adc = ADC(Pin(34))
adc.atten(ADC.ATTN_11DB)
adc.width(ADC.WIDTH_12BIT)

pinlist = [15, 2, 4, 5, 18, 19, 21, 22, 23, 36, 39, 35, 32, 33, 25, 26, 27, 14, 12, 13] # Pin 34 used for ADC so left out of list

logger.info("SETUP PIN {0}".format(pinlist[0]))
sleep(5)
for i, dtPin in enumerate(pinlist):
    period = Encoder(dtPin)
    for _ in range(4):
        if period.getdata() is not None: logger.info("Pin {0} freq:{1:.1f} Hz".format(dtPin, 1000000/period.getdata()))
        sleep(1)
    if i < (len(pinlist)-1):
        print("CHANGE TO PIN {0}".format(pinlist[i+1]))
    sleep(5)

logger.info("SETUP PIN {0}".format(pinlist[0]))
sleep(5)
logger.info("PIN, IN_PUP, IN_PUP_V, IN_PDOWN, IN_PDOWN_V, OUT_LO, OUT_HI")
for i, testpin in enumerate(pinlist):
    #PIN OUT TESTING
    volt_out_lo = "na"
    volt_out_hi = "na"
    if testpin < 34:
        test_out = Pin(testpin, Pin.OUT)
        test_out.value(0)
        sleep(0.2)
        volt_out_lo = valmap(adc.read(), 0, 4095, 0, 3.3)
        logger.debug("{0}, OUT, 0, {1}".format(testpin, valmap(adc.read(), 0, 4095, 0, 3.3)))
        test_out.value(1)
        sleep(0.2)
        volt_out_hi = valmap(adc.read(), 0, 4095, 0, 3.3)
        logger.debug("{0}, OUT, 1, {1}".format(testpin, valmap(adc.read(), 0, 4095, 0, 3.3)))
        sleep(0.5)

    #PIN IN TESTING
    test_in = Pin(testpin, Pin.IN, Pin.PULL_UP)
    sleep(0.2)
    test_in_up, volt_in_up = test_in.value(), valmap(adc.read(), 0, 4095, 0, 3.3)
    logger.debug("{0}, IN, PULLED_UP, {1}, {2}".format(testpin, valmap(adc.read(), 0, 4095, 0, 3.3), test_in.value()))
    test_in = Pin(testpin, Pin.IN, Pin.PULL_DOWN)
    sleep(0.2)
    test_in_dwn, volt_in_dwn = test_in.value(), valmap(adc.read(), 0, 4095, 0, 3.3)
    logger.debug("{0}, IN, PULLED_DOWN, {1}, {2}".format(testpin, valmap(adc.read(), 0, 4095, 0, 3.3), test_in.value()))
    logger.info("{0}, {1}, {2:.2f}, {3}, {4:.2f}, {5}, {6}".format(testpin, test_in_up, volt_in_up, test_in_dwn, volt_in_dwn, volt_out_lo, volt_out_hi))
    if i < (len(pinlist)-1):
        print("CHANGE TO PIN {0}".format(pinlist[i+1]))
    sleep(5)

'''
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