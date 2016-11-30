import subprocess
from threading import Thread
from time import sleep

class Hutschiene(Thread):
    def __init__(self):
        super(Hutschiene, self).__init__()
        self.blink_run = False
        pass

    def set_orange_light(self, state):
        if(state == True):
            subprocess.call("/home/canbus/wiringPi/orange_an.sh")
        else:
            subprocess.call("/home/canbus/wiringPi/orange_aus.sh")

    def set_red_light(self, state, blink=False):
        if blink:
            if self.blink_run is False:
                self.start()


    def red_light_blink(self, duration=30):
        for i in range(0,int((duration/4))):
            subprocess.call("/home/canbus/wiringPi/drehLampe_an.sh")
            sleep(2)
            subprocess.call("/home/canbus/wiringPi/drehLampe_aus.sh")
            sleep(2)


    def run(self):
        self.blink_run = True
        self.red_light_blink()
        self.blink_run = False

