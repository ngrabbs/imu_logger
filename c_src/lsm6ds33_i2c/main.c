/* 
default address       : 6A
temp or something else: 1C */
#include <stdio.h>
#include <stddef.h>
#include <limits.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"

// I2C address
static const uint8_t LSM6DS33_ADDR = 0x6A;

// Registers
static const uint8_t REG_DEVID = 0x0F;
static const uint8_t REG_POWER_CTL = 0x2D;
static const uint8_t REG_DATAX0 = 0x32;
static const uint8_t CTRL1_XL = 0x10;
static const uint8_t OUT_TEMP_L = 0x20;
static const uint8_t OUT_TEMP_H = 0x21;

static const uint8_t CTRL2_G = 0x11;

static const uint8_t OUTX_L_G = 0x22;
static const uint8_t OUTX_H_G = 0x23;
static const uint8_t OUTY_L_G = 0x24;
static const uint8_t OUTY_H_G = 0x25;
static const uint8_t OUTZ_L_G = 0x26;
static const uint8_t OUTZ_H_G = 0x27;

static const uint8_t STATUS_REG = 0x1E;

// Other constants
static const uint8_t DEVID = 0x69;
static const float SENSITIVITY_2G = 1.0 / 256;  // (g/LSB)
static const float EARTH_GRAVITY = 9.80665;     // Earth's gravity in [m/s^2]

/*******************************************************************************
 * Function Declarations
 */
int reg_write(i2c_inst_t *i2c, 
                const uint addr, 
                const uint8_t reg, 
                uint8_t *buf,
                const uint8_t nbytes);

int reg_read(   i2c_inst_t *i2c,
                const uint addr,
                const uint8_t reg,
                uint8_t *buf,
                const uint8_t nbytes);

float get_temp( i2c_inst_t *i2c );

void get_accel( i2c_inst_t *i2c, float *acc_x_f, float *acc_y_f, float *acc_z_f);

/*******************************************************************************
 * Function Definitions
 */

// Write 1 byte to the specified register
int reg_write(  i2c_inst_t *i2c, 
                const uint addr, 
                const uint8_t reg, 
                uint8_t *buf,
                const uint8_t nbytes) {

    int num_bytes_read = 0;
    uint8_t msg[nbytes + 1];

    // Check to make sure caller is sending 1 or more bytes
    if (nbytes < 1) {
        return 0;
    }

    // Append register address to front of data packet
    msg[0] = reg;
    for (int i = 0; i < nbytes; i++) {
        msg[i + 1] = buf[i];
    }

    // Write data to register(s) over I2C
    i2c_write_blocking(i2c, addr, msg, (nbytes + 1), false);

    return num_bytes_read;
}

// Read byte(s) from specified register. If nbytes > 1, read from consecutive
// registers.
int reg_read(  i2c_inst_t *i2c,
                const uint addr,
                const uint8_t reg,
                uint8_t *buf,
                const uint8_t nbytes) {

    int num_bytes_read = 0;

    // Check to make sure caller is asking for 1 or more bytes
    if (nbytes < 1) {
        return 0;
    }

    // Read data from register(s) over I2C
    i2c_write_blocking(i2c, addr, &reg, 1, true);
    num_bytes_read = i2c_read_blocking(i2c, addr, buf, nbytes, false);

    return num_bytes_read;
}

float get_temp(i2c_inst_t *i2c)
{
    uint8_t data[1];
    int byteCount = reg_read(i2c, LSM6DS33_ADDR, OUT_TEMP_L, data, 2);
    int16_t rawTemp = data[1] << 8 | data[0];
    float temperature_sensitivity = 256.0; // Temp sensor sensitivity in LSB/degC 
    // (0°C × 9/5) + 32 = 32°F
    return (((rawTemp / temperature_sensitivity) + 25.0) * 9/5) + 32; // return this for F
//    return (rawTemp / temperature_sensitivity) + 25.0; // return this for C
}

void get_accel( i2c_inst_t *i2c, float *acc_x_f, float *acc_y_f, float *acc_z_f)
{
    uint8_t data[6];
    int byteCount = reg_read(i2c, LSM6DS33_ADDR, OUTX_L_G, data, 6);
    int16_t rawXaccel = data[1] << 8 | data[0];
    int16_t rawYaccel = data[3] << 8 | data[2];
    int16_t rawZaccel = data[5] << 8 | data[4];
    printf("x: %d y: %d z: %d\n", rawXaccel, rawYaccel, rawZaccel);

}

/*******************************************************************************
 * Main
 */
int main() {
    
    /* I think that if you set a control register you have to do a reset... */

    int16_t acc_x;
    int16_t acc_y;
    int16_t acc_z;
    float acc_x_f;
    float acc_y_f;
    float acc_z_f;

    // Ports
    i2c_inst_t *i2c = i2c1;

    // Buffer to store raw reads
    uint8_t data[6];

    // Initialize chosen serial port
    stdio_init_all();

    //Initialize I2C port at 400 kHz
    i2c_init(i2c, 400 * 1000);

    // This example will use I2C0 on the default SDA and SCL pins (GP4, GP5 on a Pico)
    i2c_init(i2c_default, 100 * 1000);
    gpio_set_function(PICO_DEFAULT_I2C_SDA_PIN, GPIO_FUNC_I2C);
    gpio_set_function(PICO_DEFAULT_I2C_SCL_PIN, GPIO_FUNC_I2C);
    gpio_pull_up(PICO_DEFAULT_I2C_SDA_PIN);
    gpio_pull_up(PICO_DEFAULT_I2C_SCL_PIN);

    // Make the I2C pins available to picotool
    //bi_decl(bi_2pins_with_func(PICO_DEFAULT_I2C_SDA_PIN, PICO_DEFAULT_I2C_SCL_PIN, GPIO_FUNC_I2C));

    // Read device ID to make sure that we can communicate with the ADXL343
    reg_read(i2c, LSM6DS33_ADDR, REG_DEVID, data, 1);
    if (data[0] != DEVID) {
        printf("ERROR: Could not communicate with ADXL343\r\n");
        while (true);
    }

    while(true)
    {
        printf("%f\n", get_temp(i2c));
        sleep_ms(1000);
    
        get_accel(i2c, &acc_x_f, &acc_y_f, &acc_z_f);
    
    }

}