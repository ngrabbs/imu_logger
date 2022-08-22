import board
import digitalio
import displayio
import busio
import terminalio
import time
import sys
import struct
from adafruit_debouncer import Debouncer
from adafruit_datetime import datetime
#from adafruit_display_text import label
#import adafruit_displayio_ssd1306

########### BEGING UART ############
uart = busio.UART(board.TX, board.RX, baudrate=115200)
########### END UART ###############

########### BEGIN IMU ##############
from adafruit_lsm6ds import Rate, AccelRange, GyroRange
#from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lsm6ds.lsm6ds33 import LSM6DS33 as LSM6DS
# from adafruit_lsm6ds.lsm6dso32 import LSM6DSO32 as LSM6DS
# from adafruit_lsm6ds.ism330dhcx import ISM330DHCX as LSM6DS

i2c = board.I2C()
sensor = LSM6DS(i2c)
sensor.accelerometer_range = AccelRange.RANGE_2G
sensor.gyro_range = GyroRange.RANGE_125_DPS
sensor.accelerometer_data_rate = Rate.RATE_1_6_HZ
sensor.gyro_data_rate = Rate.RATE_1_6_HZ
########### END IMU ##############

########### BUTTON ###############
SWITCH_PIN = board.A1
RECORD_TIME = 1

switch_io = digitalio.DigitalInOut(SWITCH_PIN)
switch_io.direction = digitalio.Direction.INPUT
switch_io.pull = digitalio.Pull.UP
switch = Debouncer(switch_io)
########### END BUTTON ###########

###### Helper Functions ######

def create_file():
    now = datetime.now()
    filename = "imu_{}{}{}_{}{}{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
    try:
        fp = open("/{}.txt".format(filename), "w")
        fp.write("START: {}\r\n".format(now))
    except Exception as e:
        print(e)
        return False
    return fp

###### Classes ######
class DisplayHandler(object):
    def __init__(self):
        self.text = None
        displayio.release_displays()
        self.display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
        self.display = adafruit_displayio_ssd1306.SSD1306(self.display_bus, width=128, height=32)
        self.splash = displayio.Group()
        self.display.show(self.splash)
    
    def update(self, text):
        if self.text != text:
            self.text = text
            text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00, x=1, y=15)
            self.display.show(text_area)

class StateMachine(object):

    def __init__(self):
        self.state = None
        self.states = {}
        self.error = False

    def add_state(self, state):
        self.states[state.name] = state

    def go_to_state(self, state_name):
        if self.state:
            print('Exiting %s' % (self.state.name))
            self.state.exit(self)
        self.state = self.states[state_name]
        print('Entering %s' % (self.state.name))
        self.state.enter(self)

    def update(self):
        if self.state:
            #print('Updating %s' % (self.state.name))
            #if not self.error:
                #display.update(self.state.name)
                #display.update(self.state.name)
            
            self.state.update(self)

class State(object):

    def __init__(self):
        pass

    @property
    def name(self):
        return ''

    def enter(self, machine):
        pass

    def exit(self, machine):
        pass

    def update(self, machine):
        return True

class IdleState(State):

    def __init__(self):
        super().__init__()

    @property
    def name(self):
        return 'idle'

    def enter(self, machine):
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        if switch.fell:
            machine.go_to_state('armed')

# TO-DO: Create arm state
# Trigger indle -> trigger pull
class ArmedState(State):

    def __init__(self):
        super().__init__()

    @property
    def name(self):
        return 'armed'

    def enter(self, machine):
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        if State.update(self, machine):
            if switch.rose:
                machine.go_to_state('recording')

class RecordingState(State):
    
    def __init__(self):
        super().__init__()

    @property
    def name(self):
        return 'recording'

    def enter(self, machine):
        State.enter(self, machine)
        self.fileHandler = create_file()
        self.future = time.monotonic() + RECORD_TIME
        self.start_time = time.monotonic()
        self.array = []
        self.write_count = 0
        uart.write(bytearray(str("<")))

    def exit(self, machine):
        State.exit(self, machine)
        print("run time: ", time.monotonic() - self.start_time)
        print("data points: ", str(self.write_count))
        uart.write(bytearray(str(">")))
        for x in self.array:
             print(x)
        if self.fileHandler:
            self.fileHandler.write(str(self.array))
            self.array = []
            self.fileHandler.close()
            self.fileHandler = None

    def update(self, machine):

        if State.update(self, machine):
            now = time.monotonic()
            if now >= self.future:
                machine.go_to_state('idle')
            elif switch.fell:
                machine.go_to_state('armed')
            else:
                rounded_accel_gyro = list(round(x, 2) for x in (sensor.acceleration + sensor.gyro))
		rounded_accel_gyro.insert(0, round(time.monotonic() - self.start_time, 3))
		uart.write(bytearray(','.join(str(e) for e in rounded_accel_gyro)) + "\n")
                self.write_count = self.write_count + 1

                # if self.fileHandler:
                #     self.fileHandler.write("%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\r\n" % (sensor.acceleration + sensor.gyro))
                #     # Possible error state?
                #     print("Error state: ", machine.state.name)
                #     machine.go_to_state('idle')
                #     machine.error = True
                #     display.update("Err: unable to write")

###### MAIN ######
#display = DisplayHandler()

machine = StateMachine()
machine.add_state(IdleState())
machine.add_state(RecordingState())
machine.add_state(ArmedState())

machine.go_to_state('idle')

while True:
    switch.update()
    machine.update()
