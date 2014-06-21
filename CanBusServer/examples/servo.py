from canbus import CanBus
from time import sleep

canbus = CanBus()

client = canbus.get_can_client("seginus")
print client.set_servo(1,110)
print client.set_servo(5,90)
