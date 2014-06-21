from canbus import CanBus
from time import sleep

canbus = CanBus()

client = canbus.get_can_client("regor")
print client.set_rgb(255,0,0)
