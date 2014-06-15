# seriell einlesen ohne thread
# UNGETESTET: das wegwerfen von empfangenen zeilen, die mit ":" beginnen!

from canbus import CanBus

if __name__ == "__main__":
    import pdb; pdb.set_trace()
    canbus = CanBus()

    while True:
        altair_client = canbus.get_can_client("altair")

        altair_client.set_port(5, 1)
        altair_client.set_port(5, 0)

        analog_state = altair_client.get_analog(0)
        print 'analog state: '+analog_state
