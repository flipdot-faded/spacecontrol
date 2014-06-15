# seriell einlesen ohne thread
# UNGETESTET: das wegwerfen von empfangenen zeilen, die mit ":" beginnen!

from http_handler import HttpHandler
import SocketServer

from canbus import CanBus

PORT = 8080

if __name__ == "__main__":
    canbus = CanBus()

    httpd = SocketServer.TCPServer(("", PORT), HttpHandler)

    print "serving at port", PORT
    httpd.serve_forever()

    while True:
        altair_client = canbus.get_can_client("altair")

        altair_client.set_port(5, 1)
        altair_client.set_port(5, 0)

        analog_state = altair_client.get_analog(0)
        print 'analog state: '+analog_state
