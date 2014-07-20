import subprocess

class Hutschiene(object):
    def __init__(self):
        pass

    def set_orange_light(self, state):
        if(state == True):
            subprocess.call("/home/pi/wiringPi/orange_an.sh")
        else:
            subprocess.call("/home/pi/wiringPi/orange_aus.sh")

