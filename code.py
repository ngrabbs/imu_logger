import board
import digitalio
import time
from adafruit_debouncer import Debouncer
from adafruit_datetime import datetime

SWITCH_PIN = board.A1
RECORD_TIME = 10

switch_io = digitalio.DigitalInOut(SWITCH_PIN)
switch_io.direction = digitalio.Direction.INPUT
switch_io.pull = digitalio.Pull.UP
switch = Debouncer(switch_io)

###### Helper Functions ######

def check_space():
    # Is this possible?
    return True

def create_file():
    now = datetime.now()
    filename = "imu_{}{}{}_{}{}{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
    try:
        fp = open("/{}.txt".format(filename), "w")
        return fp
    except Exception as e:
        print(e)
        return None

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
            print('Updating %s' % (self.state.name))
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
        self.fileHandler = create_file()
        self.future = time.monotonic() + RECORD_TIME

    def exit(self, machine):
        State.exit(self, machine)
        if self.fileHandler:
            self.fileHandler.close()
            self.fileHandler = None

    def update(self, machine):
        if State.update(self, machine):
            now = time.monotonic()
            if now >= self.future:
                machine.go_to_state('idle')
            if switch.fell:
                machine.go_to_state('recording')

            # If no conditions, write the file
            # Write Gyro Data
            if self.fileHandler:
                self.fileHandler.write("{} Sensor Data\r\n".format(time.monotonic()))
                
###### MAIN ######

machine = StateMachine()
machine.add_state(IdleState())
machine.add_state(RecordingState())

machine.go_to_state('idle')

while True:
    switch.update()
    machine.update()