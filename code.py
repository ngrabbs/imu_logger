import board
import digitalio
import displayio
import terminalio
import time
from adafruit_debouncer import Debouncer
from adafruit_datetime import datetime

########### BEGIN IMU ##############
from adafruit_lsm6ds import Rate, AccelRange, GyroRange
#from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lsm6ds.lsm6ds33 import LSM6DS33 as LSM6DS
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
#SWITCH_PIN = board.A1
SWITCH_PIN = board.D6
RECORD_TIME = 10

switch_io = digitalio.DigitalInOut(SWITCH_PIN)
switch_io.direction = digitalio.Direction.INPUT
switch_io.pull = digitalio.Pull.UP
switch = Debouncer(switch_io)
########### END BUTTON ###########

########### DISPLAY ##############
from adafruit_display_text import label
import adafruit_displayio_ssd1306
displayio.release_displays()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)

# Make the display context
splash = displayio.Group()
display.show(splash)
########### END DISPLAY ##########

###### Helper Functions ######

def check_space():
    # Is this possible?
    return True

def create_file():
    now = datetime.now()
    filename = "imu_{}{}{}_{}{}{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
    try:
        with open("/{}.txt".format(filename), "w") as fp:
            fp.write("{}\r\n".format(now))
    except Exception as e:
        print(e)
    return filename

###### Classes ######
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
#            print('Updating %s' % (self.state.name))
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
            machine.go_to_state('recording')

class RecordingState(State):
    
    def __init__(self):
        super().__init__()

    @property
    def name(self):
        return 'recording'

    def enter(self, machine):
        State.enter(self, machine)
        self.filename = create_file()
        self.future = time.monotonic() + RECORD_TIME
	    self.data = []

    def exit(self, machine):
        State.exit(self, machine)
        self.filename = None
        self.data = None
        if self.filename:
            write open("/{}.txt".format(self.filename), "a") as fp:
                # Write Gyro Data
	            for x in self.data:
                    #fp.write("Accel X:%.2f Y:%.2f Z:%.2f ms^2 Gyro X:%.2f Y:%.2f Z:%.2f radians/s\r\n" % (sensor.acceleration + sensor.gyro))
                    print(x)
                    fp.write("Accel X:%.2f Y:%.2f Z:%.2f ms^2\r\n" % (sensor.acceleration))

    def update(self, machine):
        if State.update(self, machine):
            now = time.monotonic()
            if now >= self.future:
                machine.go_to_state('idle')
            if switch.fell:
                machine.go_to_state('recording')
            #if self.data ## something different needs to happen here
            self.data.append(sensor.acceleration)
            ## doesnt work very well ^^^

###### MAIN ######

machine = StateMachine()
machine.add_state(IdleState())
machine.add_state(RecordingState())

machine.go_to_state('idle')

while True:
    switch.update()
    machine.update()