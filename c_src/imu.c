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
