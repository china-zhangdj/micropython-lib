import umachine


PINNO_OFFSET_MAP = {
'PA':0,
'PB':32,
'PC':64,
'PD':96,
'PE':128,
'PF':160,
'PG':192,
'PH':224,
'PI':256,
'PJ':288,
'PK':320,
'PL':352,
'PM':384,
'PN':416,
'PO':448
}

def pinnane_to_pinno(pinname:str) :
    '''
    IO 转 PIN 号
    '''
    if len(pinname) < 3 :
        raise IOError("len pin name must more than 3 !")
    group = pinname[:2]
    offset = 0
    if group in PINNO_OFFSET_MAP.keys() :
        offset = PINNO_OFFSET_MAP[group]
        pass
    else:
        raise IOError("pin group must in A-O !")
    number = 0
    try :
        number = int(pinname[2:])
    except Exception as e :
        raise IOError("pin number must can conv to number !")
    pinno = offset + number
    return pinno



class Pin(umachine.PinBase):
    IN = "in"
    OUT = "out"
    PULL_UP = 1
    PULL_DOWN = 2
    PULL_NO = 0
    DLEVEL_0 = 0
    DLEVEL_1 = 1
    DLEVEL_2 = 2
    DLEVEL_3 = 3

    def __init__(self, pname:str,dir=IN,pull=PULL_NO,dlevel=DLEVEL_1):
        self.number = pinnane_to_pinno(pname)
        pref = "/sys/class/gpio/gpio{}/".format(self.number)
        dirf = pref + "direction"
        try:
            f = open(dirf, "w")
        except OSError:
            with open("/sys/class/gpio/export", "w") as f:
                f.write(str(self.number))
            f = open(dirf, "w")
        f.write(dir)
        f.close()
        try:
            with open("/sys/kernel/debug/sunxi_pinctrl/sunxi_pin", "w") as f :
                f.write(pname)
            with open("/sys/kernel/debug/sunxi_pinctrl/pull","w") as f :
                f.write("{} {}".format(pname,pull))
            with open("/sys/kernel/debug/sunxi_pinctrl/dlevel","w") as f :
                f.write("{} {}".format(pname,dlevel))
        except OSError:
            # not support sunxi debug pin
            pass
        self.f = open(pref + "value", "r+b")

    @property
    def value(self):
        self.f.seek(0)
        return 1 if self.f.read(1) == b"1" else 0

    @value.setter
    def value(self,value:int):
        self.f.write(b"1" if value else b"0")

    def deinit(self):
        self.f.close()
        try:
            with open("/sys/class/gpio/unexport", "w") as f :
                f.write(str(self.number))
        except OSError as e :
            pass

    def __del__(self):
        self.f.close()
        try:
            with open("/sys/class/gpio/unexport", "w") as f :
                f.write(str(self.number))
        except OSError as e :
            pass



