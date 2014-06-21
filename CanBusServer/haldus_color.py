from canbus import CanBus
from time import sleep

canbus = CanBus()

client = canbus.get_can_client("haldus")
print client.set_rgb(0,255,0)
