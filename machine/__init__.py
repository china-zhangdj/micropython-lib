from umachine import *
from .timer import *
from .pin import Pin
from .serial import Serial
from .i2c import I2C
from .spi import SPI

def unique_id():
    res = os.popen("cat /sys/class/sunxi_info/sys_info").read().split("\n")[2].split(": ")[1]
    return res

