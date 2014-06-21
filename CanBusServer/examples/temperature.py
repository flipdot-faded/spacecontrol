from canbus import CanBus
from time import sleep

canbus = CanBus()

client = canbus.get_can_client("thabit")
print client.get_temp()
