from canbus import CanBus

canbus = CanBus()

client = canbus.get_can_client("serius")
antwort = client.set_port(2, 1)
