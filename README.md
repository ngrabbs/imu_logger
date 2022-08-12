# imu_logger
IMU logging tool

# Hardware
I'm using a adafruit feather [rp2040](https://www.adafruit.com/product/4884) and im programming it from a [pi400](https://www.adafruit.com/product/4795)
![hardware setup](images/hardware_setup.jpg)

# Getting started
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