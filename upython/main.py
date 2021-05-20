from machine import Pin, PWM, ADC
from time import sleep
from mytools import valmap, pcolor
import ulogging, utime, math, esp, gc, micropython, sys
from encoder import Encoder
esp.osdebug(None)
gc.collect()
micropython.alloc_emergency_exception_buf(100)
'''
Pins 32-39 - ADC
Pins 34-39 are input only, and also do not have internal pull-up resistors. But can be used for ADC
 VP(36), VN(39) are input only
Pins 6, 7, 8, 11, 16, and 17 are used for connecting the embedded flash, and are not recommended for other uses
Pins high at boot GPIO 1,3,5,6-11,14,15
Reboot - (EN) is the 3.3V enable pin. Connect to ground to restart
Pin2 is connected to internal led (fails pull_up)

According to o-scope the PWM output was accurate. But reading PWM at 10MHz had large error
'''
def run_GPIO_test(testingpins, resultsfile):
    pinlist = testingpins
    file = resultsfile
    mode = 'a'
    ulogging.basicConfig(level=10) # Change logger global settings
    logger = ulogging.getLogger(__name__)
    logger.info("GPIO Pin test on pins: {0}".format(pinlist))
    logger.info("Results written to file: {0}".format(file))
    logger.info("Pin {0} used for PWM and {1} used for adc so not included in testing".format(encoderPin, adcPin))
    with open(file, mode) as f:
        f.write("\nPin {0} used for PWM and {1} used for adc so not included in testing".format(encoderPin, adcPin))

    adc = ADC(Pin(adcPin))           # Pin 34 is used for ADC and left out of pins tested below
    adc.atten(ADC.ATTN_11DB)
    adc.width(ADC.WIDTH_12BIT)
    # Measure pin out hi/lo and then pin in with internal up/down resistor
    logger.info("I/O HI/LO AND UP/DOWN RESISTOR MEASUREMENT STARTING")
    logger.warning("CONNECT ADC PIN {0} TO {1}".format(adcPin, pinlist[0]))
    sleep(10)
    logger.info("PIN, TEST, IN_PUP/PWM_ERROR%, IN_PUP_V, IN_PDOWN, IN_PDOWN_V, OUT_LO, OUT_HI")
    with open(file, mode) as f:
        f.write("\nPIN, (freq), (duty), TEST, IN_PUP/PWM_ERROR%, IN_PUP_V, IN_PDOWN, IN_PDOWN_V, OUT_LO, OUT_HI")
    for i, testpin in enumerate(pinlist):
        #PIN OUT TESTING (HI/LOW)
        volt_out_lo = "na"
        volt_out_hi = "na"
        if testpin < 34:
            test_out = Pin(testpin, Pin.OUT)
            test_out.value(0)
            sleep(0.2)
            volt_out_lo = valmap(adc.read(), 0, 4095, 0, 3.3)
            if volt_out_lo < 0.1:
                logger.debug("{0}, OUT, 0, {1}".format(testpin, volt_out_lo))
            else:
                logger.error("{0}, OUT, 0, {1}".format(testpin, volt_out_lo))
            test_out.value(1)
            sleep(0.2)
            volt_out_hi = valmap(adc.read(), 0, 4095, 0, 3.3)
            if volt_out_hi > 3.2:
                logger.debug("{0}, OUT, 1, {1}".format(testpin, volt_out_hi))
            else:
                logger.error("{0}, OUT, 1, {1}".format(testpin, volt_out_hi))
            sleep(0.5)

        #PIN IN TESTING WITH BOTH PULLED_UP AND PULLED_DOWN
        test_in = Pin(testpin, Pin.IN, Pin.PULL_UP)
        sleep(0.2)
        test_in_up, volt_in_up = test_in.value(), valmap(adc.read(), 0, 4095, 0, 3.3)
        if volt_in_up > 3.2:
            logger.debug("{0}, IN, PULLED_UP, {1}, {2}".format(testpin, volt_in_up, test_in.value()))
        else:
            logger.error("{0}, IN, PULLED_UP, {1}, {2}".format(testpin, volt_in_up, test_in.value()))
        test_in = Pin(testpin, Pin.IN, Pin.PULL_DOWN)
        sleep(0.2)
        test_in_dwn, volt_in_dwn = test_in.value(), valmap(adc.read(), 0, 4095, 0, 3.3)
        if volt_in_dwn < 0.1:
            logger.debug("{0}, IN, PULLED_DOWN, {1}, {2}".format(testpin, volt_in_dwn, test_in.value()))
        else:
            logger.error("{0}, IN, PULLED_DOWN, {1}, {2}".format(testpin, volt_in_dwn, test_in.value()))
        logger.info("IO({0},input,output), IO, {1}, {2:.2f}, {3}, {4:.2f}, {5}, {6}".format(testpin, test_in_up, volt_in_up, test_in_dwn, volt_in_dwn, volt_out_lo, volt_out_hi))
        with open(file, mode) as f:
            f.write("\nIO({0},input,output), IO, {1}, {2:.2f}, {3}, {4:.2f}, {5}, {6}".format(testpin, test_in_up, volt_in_up, test_in_dwn, volt_in_dwn, volt_out_lo, volt_out_hi))
        if i < (len(pinlist)-1):
            logger.warning("CHANGE TO PIN {0}".format(pinlist[i+1]))
            sleep(5)


    # Create PWM signal. Can measure with o-scope or use encoder library to measure signal below    
    logger.info("PWM OUTPUT/INPUT STARTING")
    freqout = 100       # Setup pin for outputing PWM to be read by other pins
    dutyout = 512
    logger.info("PWM USING PIN {0} TO CREATE SIGNAL AT {1}Hz and DC {2}".format(encoderPin, freqout, dutyout))
    logger.warning("CONNECT PWM PIN {0} TO {1}".format(encoderPin, pinlist[0]))
    sleep(10)
    # can set frequency 1-40MHz (higher freq has lower duty resolution)
    # duty cycle from 0 to 1023 (0-100%) duty cycle
    # can use pwm.freq() and pwm.duty() to retrieve current settings.
    frequency = [100, 1000, 10000]
    for i, pin in enumerate(pinlist):
        period = Encoder(encoderPin)  # Setup pin for reading PWM from other pins
        if pin < 34:
            pwmPin = PWM(Pin(pin))
            # one line PWM(Pin(2), freq=500, duty=512)
            for freq in frequency:
                pwmPin.freq(freq)
                for duty_cycle in range(1, 1024, 73):
                    pwmPin.duty(duty_cycle)
                    sleep(0.05)
                    dataArr = []
                    for _ in range(3):
                        data = period.getdata()
                        if data is not None:
                            logger.debug("Pin {0} period:{1:.1f} us".format(pwmPin, data))
                            data = "{:.1f}".format(math.fabs(((freq - (1000000/data))/freq)*100)) # calculate freq error
                            dataArr.append(float(data)) 
                        sleep(0.05)
                    logger.debug("Pin {0} freq delta:{1} %".format(pwmPin, dataArr))
                    if len(dataArr) > 0:
                        dataAve = sum(dataArr)/len(dataArr)
                        logger.info("{0}, PWM_OUTPUT_ERROR%, {1:.1f}".format(pwmPin, dataAve))
                        with open(file, mode) as f:
                            f.write("\n{0}, PWM_OUTPUT_ERROR%, {1:.1f}".format(pwmPin, dataAve))
                    sleep(0.005)
            pwmPin.deinit()

        pwmOUT = PWM(Pin(encoderPin), freq=freqout, duty=dutyout)
        periodtest = Encoder(pin)
        periodArr = []
        for _ in range(4):
            if periodtest.getdata() is not None:
                data = math.fabs(1000000/periodtest.getdata())
                logger.debug("Pin {0} freq:{1:.1f} Hz".format(pin, data))
                periodArr.append(data)
            sleep(0.05)
        if len(periodArr) > 0: 
            logger.info("PWM({0}, freq={1}, duty={2}), PWM_READ_HZ, {3:.1f}".format(pin, freqout, dutyout, ((freq-sum(periodArr)/len(periodArr))/freq*100)))
            with open(file, mode) as f:
                f.write("\nPWM({0}, freq={1}, duty={2}), PWM_READ_HZ, {3:.1f}".format(pin, freqout, dutyout, ((freq-sum(periodArr)/len(periodArr))/freq*100)))
        if i < (len(pinlist)-1):
            logger.warning("CHANGE TO PIN {0}".format(pinlist[i+1]))
            sleep(5)
        pwmOUT.deinit()

encoderPin = 15
adcPin = 34
pinlist = [2, 4, 5, 18, 19, 21, 22, 23, 36, 39, 35, 32, 33, 25, 26, 27, 14, 12, 13] # Pin 34 used for ADC and 15 used for PWM so left out of list
results = str(input("{0}Enter results file name: {1}".format(pcolor.YELLOW, pcolor.ENDC)))
with open(results, 'w') as f:
        f.write("ESP32 GPIO TEST ON {0}".format(rtcdate(rtc.datetime())))
while 1:
    print("{0}1 - Run GPIO test on all pins. New results file will be created{1}".format(pcolor.BLUE, pcolor.ENDC))
    print("{0}2 - Run GPIO test on a single pin. Results file will be appended{1}".format(pcolor.DBLUE, pcolor.ENDC))
    print("{0}3 - EXIT{1}".format(pcolor.RED, pcolor.ENDC))
    val = int(input("Enter choice: "))
    if val == 1:
        run_GPIO_test(pinlist, results)
    elif val == 2:
        pinlist = []
        pinlist.append(int(input("Enter GPIO pin to test: ")))
        run_GPIO_test(pinlist, results)
    elif val == 3:
        sys.exit()