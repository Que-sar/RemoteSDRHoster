#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/gpio.h>

#define LED1 17 
#define LED2 27  
#define LED3 22  

static int __init gpio_init(void) {

    // LED 1 setup
    gpio_request(LED1, "sysfs");
    gpio_direction_output(LED1, 0);
    gpio_export(LED1, false);

    // LED 2 setup
    gpio_request(LED2, "sysfs");
    gpio_direction_output(LED2, 0);
    gpio_export(LED2, false);

    // LED 3 setup
    gpio_request(LED3, "sysfs");
    gpio_direction_output(LED3, 0);
    gpio_export(LED3, false);

    return 0;
}

static void __exit gpio_exit(void) {
    gpio_unexport(LED1);
    gpio_free(LED1);
    gpio_unexport(LED2);
    gpio_free(LED2);
    gpio_unexport(LED3);
    gpio_free(LED3);
}

module_init(gpio_init);
module_exit(gpio_exit);
