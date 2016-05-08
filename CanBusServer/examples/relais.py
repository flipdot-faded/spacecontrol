from canbus import CanBus
from time import sleep

canbus = CanBus()

client = canbus.get_can_client("regulus")
print client.set_port(0,1)
#sleep(1)
#print client.set_port(0,0)


