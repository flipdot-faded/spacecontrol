from canbus import CanBus
from time import sleep

canbus = CanBus()

client = canbus.get_can_client("theemin")
print client.send_cmd("getActTemp")
