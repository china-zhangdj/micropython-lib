import lvgl as lv
import _thread

class touch:
    def __init__(self,path="/dev/input/event1",w=240,h=240,wp=1,hp=1):
        '''
        创建触摸设备
        :param path: 触摸设备文件
        :param w: 屏幕宽度
        :param h: 屏幕高度
        :param wp: 宽度比例
        :param hp: 高度比例
        '''
        self.dev = path
        self.x = 0
        self.y = 0
        self.state = lv.INDEV_STATE.RELEASED
        self.th_read = _thread.start_new_thread(self.thread_read,())
        self.w = w
        self.h = h

    def thread_read(self):
        try :
            with open(self.dev,"rb") as f :
                while True:
                    res = f.read(16)
                    res = res[8:]
                    ev_type = int.from_bytes(res[0:2],"little")
                    ev_code = int.from_bytes(res[2:4],"little")
                    ev_val = int.from_bytes(res[4:],"little")
                    if ev_type == 3 and ev_code == 53 :
                        self.x = ev_val
                        if self.x > self.w :
                            self.x = self.w
                    if ev_type == 3 and ev_code == 54 :
                        self.y = 240 - ev_val
                        if self.y < 0 :
                            self.y=0
                        if self.y > self.h :
                            self.y = self.h
                    elif ev_type == 1 and ev_code == 330:
                        if ev_val == 0 :
                            self.state = lv.INDEV_STATE.RELEASED
                        else :
                            self.state = lv.INDEV_STATE.PRESSED
        except Exception as e :
            print("touch indev error: {}".format(e))
            pass

    def driver_touch_read(self, indev_drv, data) -> int:
        data.point.x = self.x
        data.point.y = self.y
        # print("x={} y={} state={}".format(data.point.x,data.point.y,data.state))
        data.state = self.state
        return True

