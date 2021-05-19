import esp, machine
from mytools import rtcdate
esp.osdebug(None)
#import webrepl
#webrepl.start()

# SET CPU FREQUENCY
CPUFREQ = 240000000  # Can set to 160000000 or 80000000 to save power, but loop time will be much slower
machine.freq(CPUFREQ)

# SET UP REAL TIME CLOCK. EITHER MANUALLY SET DATETIME OR USE LOCAL NETWORK
rtc = machine.RTC()
#rtc.datetime((2021, 5, 6, 0, 12, 55, 0, 0))  # If using local network time comment out rtc.datetime(xxx)
#(year, month, day, weekday, hours, minutes, seconds, subseconds)
print('RTC datetime: {0}'.format(rtcdate(rtc.datetime())))