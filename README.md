# imu_logger
IMU logging tool

# Hardware
I'm using a adafruit feather [rp2040](https://www.adafruit.com/product/4884) and im programming it from a [pi400](https://www.adafruit.com/product/4795)
![hardware setup](images/hardware_setup.jpg)

# Getting started
## Blink / Console
First plug your RP2040 into your raspberry pi as shown in the hardware section

After you plugin you can run the dmesg command and see what the device handle is, in my case its 'sdb'
```shell
pi@raspberrypi:/media $ dmesg | grep '] sd'
[43206.732827] sd 1:0:0:0: Attached scsi generic sg0 type 0
[43206.733961] sd 1:0:0:0: [sdb] 14337 512-byte logical blocks: (7.34 MB/7.00 MiB)
[43206.736056] sd 1:0:0:0: [sdb] Write Protect is off
[43206.736072] sd 1:0:0:0: [sdb] Mode Sense: 03 00 00 00
[43206.738556] sd 1:0:0:0: [sdb] No Caching mode page found
[43206.738571] sd 1:0:0:0: [sdb] Assuming drive cache: write through
[43206.810579] sd 1:0:0:0: [sdb] Attached SCSI removable disk
```

Next I mount the file system to media
```shell
pi@raspberrypi:~ $ sudo mount /dev/sdb1 /media
pi@raspberrypi:~ $ ls /media
boot_out.txt  code.py  lib
pi@raspberrypi:~ $
```

The sample "blink" program looks like this:
```python
pi@raspberrypi:/media $ cat code.py
import time
import board
import neopixel

pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixels.brightness = 0.1

while True:
    print("Change\n")
    pixels.fill((255, 0, 0))
    time.sleep(0.5)
    pixels.fill((0, 0, 0))
    time.sleep(0.5)
pi@raspberrypi:/media $
```

Another important peice for testing this setup is being able to get data from the console.  I put a print statement in the code and we can view it by using screen:
```
pi@raspberrypi:~ $ ls -la /dev/ttyA*
crw-rw---- 1 root dialout 166,  0 Aug 12 14:49 /dev/ttyACM0
crw-rw---- 1 root dialout 204, 64 Aug 12 02:17 /dev/ttyAMA0
pi@raspberrypi:~ $ screen /dev/ttyACM0 115200
Change

Change

Change

Change

Change

Change

Change

Change

Change
```

## lsm6ds33 / console
This example we'll get the output from a lsm6ds33 that is plugged in via the STEMMA qt connector
First copy the library from adafruits github repo:
```
pi@raspberrypi:~ $ git clone https://github.com/adafruit/Adafruit_CircuitPython_Register.git
Cloning into 'Adafruit_CircuitPython_Register'...
remote: Enumerating objects: 662, done.
remote: Counting objects: 100% (144/144), done.
remote: Compressing objects: 100% (74/74), done.
remote: Total 662 (delta 71), reused 139 (delta 68), pack-reused 518
Receiving objects: 100% (662/662), 170.75 KiB | 1.42 MiB/s, done.
Resolving deltas: 100% (368/368), done.
pi@raspberrypi:~ $ cd Adafruit_CircuitPython_Register/
pi@raspberrypi:~/Adafruit_CircuitPython_Register $ ls
adafruit_register  CODE_OF_CONDUCT.md  docs  examples  LICENSE  LICENSES  optional_requirements.txt  pyproject.toml  README.rst  README.rst.license  requirements.txt
pi@raspberrypi:~/Adafruit_CircuitPython_Register $ sudo cp -r adafruit_register /media/lib/
pi@raspberrypi:~/Adafruit_CircuitPython_Register $ cd ..
pi@raspberrypi:~ $ git clone https://github.com/adafruit/Adafruit_CircuitPython_LSM6DS.git
Cloning into 'Adafruit_CircuitPython_LSM6DS'...
remote: Enumerating objects: 680, done.
remote: Counting objects: 100% (119/119), done.
remote: Compressing objects: 100% (68/68), done.
remote: Total 680 (delta 68), reused 74 (delta 51), pack-reused 561
Receiving objects: 100% (680/680), 159.73 KiB | 1.44 MiB/s, done.
Resolving deltas: 100% (405/405), done.
pi@raspberrypi:~ $ ls
Adafruit_CircuitPython_LSM6DS  code.py.bak  Desktop  Documents  Downloads  fpga  Music  openbox-themes  Pictures  Public  Templates  venv  Videos
pi@raspberrypi:~ $ cd Adafruit_CircuitPython_LSM6DS/
pi@raspberrypi:~/Adafruit_CircuitPython_LSM6DS $ ls
adafruit_lsm6ds  CODE_OF_CONDUCT.md  docs  examples  LICENSE  LICENSES  optional_requirements.txt  pyproject.toml  README.rst  README.rst.license  requirements.txt
pi@raspberrypi:~/Adafruit_CircuitPython_LSM6DS $ sudo cp -r adafruit_lsm6ds /media/lib/
pi@raspberrypi:~/Adafruit_CircuitPython_LSM6DS $```

Second setup some example code in code.py (Note you may have to tweak what device you have):
```python
# SPDX-FileCopyrightText: Copyright (c) 2020 Bryan Siepert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
import time
import board

# pylint:disable=no-member
from adafruit_lsm6ds import Rate, AccelRange, GyroRange

#from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS

from adafruit_lsm6ds.lsm6ds33 import LSM6DS33 as LSM6DS
# from adafruit_lsm6ds.lsm6dso32 import LSM6DSO32 as LSM6DS
# from adafruit_lsm6ds.ism330dhcx import ISM330DHCX as LSM6DS

i2c = board.I2C()  # uses board.SCL and board.SDA
sensor = LSM6DS(i2c)

sensor.accelerometer_range = AccelRange.RANGE_8G
print(
    "Accelerometer range set to: %d G" % AccelRange.string[sensor.accelerometer_range]
)

sensor.gyro_range = GyroRange.RANGE_2000_DPS
print("Gyro range set to: %d DPS" % GyroRange.string[sensor.gyro_range])

sensor.accelerometer_data_rate = Rate.RATE_1_66K_HZ
# sensor.accelerometer_data_rate = Rate.RATE_12_5_HZ
print("Accelerometer rate set to: %d HZ" % Rate.string[sensor.accelerometer_data_rate])

sensor.gyro_data_rate = Rate.RATE_1_66K_HZ
print("Gyro rate set to: %d HZ" % Rate.string[sensor.gyro_data_rate])

while True:
    print(
        "Accel X:%.2f Y:%.2f Z:%.2f ms^2 Gyro X:%.2f Y:%.2f Z:%.2f radians/s"
        % (sensor.acceleration + sensor.gyro)
    )
    time.sleep(0.05)
```

After you have setup the code you can access the console and should recieve output:
```
screen /dev/ttyACM0 115200
Accel X:0.30 Y:5.19 Z:8.46 ms^2 Gyro X:0.06 Y:-0.15 Z:-0.09 radians/s
Accel X:0.18 Y:5.27 Z:8.44 ms^2 Gyro X:0.08 Y:-0.15 Z:-0.10 radians/s
Accel X:0.28 Y:5.25 Z:8.44 ms^2 Gyro X:0.05 Y:-0.15 Z:-0.08 radians/s
Accel X:0.15 Y:5.24 Z:8.34 ms^2 Gyro X:0.08 Y:-0.15 Z:-0.09 radians/s
Accel X:0.26 Y:5.24 Z:8.46 ms^2 Gyro X:0.05 Y:-0.14 Z:-0.09 radians/s
Accel X:0.17 Y:5.21 Z:8.45 ms^2 Gyro X:0.06 Y:-0.14 Z:-0.09 radians/s
Accel X:0.27 Y:5.24 Z:8.36 ms^2 Gyro X:0.05 Y:-0.14 Z:-0.08 radians/s
Accel X:0.26 Y:5.32 Z:8.50 ms^2 Gyro X:0.05 Y:-0.13 Z:-0.09 radians/s
Accel X:0.27 Y:5.24 Z:8.45 ms^2 Gyro X:0.04 Y:-0.14 Z:-0.09 radians/s
Accel X:0.25 Y:5.27 Z:8.26 ms^2 Gyro X:0.05 Y:-0.13 Z:-0.09 radians/s
Accel X:0.28 Y:5.23 Z:8.42 ms^2 Gyro X:0.04 Y:-0.14 Z:-0.09 radians/s
Accel X:0.26 Y:5.25 Z:8.44 ms^2 Gyro X:0.05 Y:-0.14 Z:-0.09 radians/s
Traceback (most recent call last):
  File "code.py", line 39, in <module>
KeyboardInterrupt:

Code done running.

Press any key to enter the REPL. Use CTRL-D to reload.
```