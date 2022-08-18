import board
import digitalio
import displayio
import terminalio
import time
from adafruit_debouncer import Debouncer
from adafruit_datetime import datetime
from adafruit_display_text import label
import adafruit_displayio_ssd1306

########### BEGIN IMU ##############
from adafruit_lsm6ds import Rate, AccelRange, GyroRange
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
#from adafruit_lsm6ds.lsm6ds33 import LSM6DS33 as LSM6DS
# from adafruit_lsm6ds.lsm6dso32 import LSM6DSO32 as LSM6DS
# from adafruit_lsm6ds.ism330dhcx import ISM330DHCX as LSM6DS

i2c = board.I2C()
sensor = LSM6DS(i2c)
sensor.accelerometer_range = AccelRange.RANGE_8G
sensor.gyro_range = GyroRange.RANGE_2000_DPS
sensor.accelerometer_data_rate = Rate.RATE_1_66K_HZ
# sensor.accelerometer_data_rate = Rate.RATE_12_5_HZ
sensor.gyro_data_rate = Rate.RATE_1_66K_HZ
########### END IMU ##############

########### BUTTON ###############
SWITCH_PIN = board.D6
RECORD_TIME = 10

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
            text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00, x=28, y=15)
            self.display.show(text_area)


class StateMachine(object):

    def __init__(self):
        self.state = None
        self.states = {}

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
            display.update(self.state.name)
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

    def exit(self, machine):
        State.exit(self, machine)
        if self.fileHandler:
            self.fileHandler = None

    def update(self, machine):
        if State.update(self, machine):
            now = time.monotonic()
            if now >= self.future:
                machine.go_to_state('idle')
            if switch.fell:
                machine.go_to_state('armed')
            
            if self.fileHandler:
                self.fileHandler.write("AX:%.2fAY,:%.2f,AZ:%.2f,GX:%.2f,GY:%.2f,GZ:%.2f\r\n" % (sensor.acceleration + sensor.gyro))
            else:
                # Possible error state?
                display.update("Error: no filehandler")
                #print("No filehandler")
                #machine.go_to_state('idle')

###### MAIN ######
display = DisplayHandler()

machine = StateMachine()
machine.add_state(IdleState())
machine.add_state(RecordingState())
machine.add_state(ArmedState())

machine.go_to_state('idle')

while True:
    switch.update()
    machine.update()