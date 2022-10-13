# C Development Guide

# Goals of project:
1. practice developing embedded C
2. log imu data from:
    a) model rockets
    b) race cars
3. support multiple types of imu
4. use as few canned libraries as possible

# User Interface:
Users should be able to interact with a menu system over:
1. lora
2. uart
3. spi
4. i2c

User can select parameters for log:
1. log duration
2. parameters to log (accel x/y/z, gyro x/y/z)
3. give a name for the log
4. frequency to poll the IMU (should also be configured on the IMU)

User can recover log over supported interfaces in .csv format

# Triggering mechanism
User will have the ability to arm the system and trigger the logging start

# Supported IMU types:
1. LSM6DS33 (adafruit) [LSM6DS33 Datasheet](https://www.mouser.com/datasheet/2/389/dm00157718-1798631.pdf)
2. LSM6DSOX (adafruit) [LSM6DSOX Datasheet](https://www.st.com/resource/en/datasheet/dm00557899.pdf)

# Development board
[Adafruit RP2040](https://www.adafruit.com/product/4884)
This board has 8MB onboard spi flash that we can store data to and recover data from

# Supporting Documentation
[DigiKey rp2040 i2c guide](https://www.digikey.com/en/maker/projects/raspberry-pi-pico-rp2040-i2c-example-with-micropython-and-cc/47d0c922b79342779cdbd4b37b7eb7e2)
[raspberry pi pico official docs](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html)
[rpi pico official datasheet](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf)
[rpi pico getting started](https://datasheets.raspberrypi.com/pico/getting-started-with-pico.pdf)
[rpi pico c/c++ sdk](https://datasheets.raspberrypi.com/pico/raspberry-pi-pico-c-sdk.pdf)

Shawn Hymel 3 part series on setting up the c sdk and vscode dev environment
[part 1 setup](https://www.youtube.com/watch?v=B5rQSoOmR5w)
[part 2 single step debug](https://www.youtube.com/watch?v=jnC5LrTx470&t=372s)
[part 3 pio](https://www.youtube.com/watch?v=JSis2NU65w8&t=19s)

