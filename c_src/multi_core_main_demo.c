#include <stdio.h>
#include "pico/stdlib.h"
#include "pico/multicore.h"

// Core to write data
void core1_entry() {
    uint32_t d;

    while (true) {
        d = multicore_fifo_pop_blocking();
        printf("Data received: %u\r\n", d);
    }
}

// Core to Poll Sensors
int main() {
    stdio_init_all();
    multicore_launch_core1(core1_entry);
    
    while (true) {
        multicore_fifo_push_blocking(1);
        sleep_ms(1000);
    }
    return 0;
}