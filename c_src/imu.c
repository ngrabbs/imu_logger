#ifndef HARDWARE_I2C_H
#define HARDWARE_I2C_H

#include "hardware/i2c.h"

#endif // HARDWARE_I2C_H

#ifndef GPIO_H
#define GPIO_H
#include "gpio.h"

#endif // GPIO_H

#ifndef STDIO_H
#define STDIO_H
#include <stdio.h>
#endif // STDIO_H

#ifndef STDDEF_H
#define STDDEF_H
#include <stddef.h>
#endif // STDDEF_H


float get_temp(i2c_inst_t *i2c, const uint8_t IMU_ADDR, const uint8_t TEMP_ADDR)
{
    uint8_t data[1];
    int byteCount = reg_read(i2c, IMU_ADDR, TEMP_ADDR, data, 2);
    int16_t rawTemp = data[1] << 8 | data[0];
    float temperature_sensitivity = 256.0; // Temp sensor sensitivity in LSB/degC 
    // (0°C × 9/5) + 32 = 32°F
    return (((rawTemp / temperature_sensitivity) + 25.0) * 9/5) + 32; // return this for F
//    return (rawTemp / temperature_sensitivity) + 25.0; // return this for C
}

void get_accel( i2c_inst_t *i2c, float *acc_x_f, float *acc_y_f, float *acc_z_f, const uint8_t IMU_ADDR, const uint8_t ACCEL_ADDR)
{
    uint8_t data[6];
    int byteCount = reg_read(i2c, IMU_ADDR, ACCEL_ADDR, data, 6);
    int16_t rawXaccel = data[1] << 8 | data[0];
    int16_t rawYaccel = data[3] << 8 | data[2];
    int16_t rawZaccel = data[5] << 8 | data[4];
    printf("x: %d y: %d z: %d\n", rawXaccel, rawYaccel, rawZaccel);

}
