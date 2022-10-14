float get_temp( i2c_inst_t *i2c, const uint8_t IMU_ADDR, const uint8_t TEMP_ADDR);

void get_accel( i2c_inst_t *i2c, float *acc_x_f, float *acc_y_f, float *acc_z_f, const uint8_t IMU_ADDR, const uint8_t ACCEL_ADDR);

