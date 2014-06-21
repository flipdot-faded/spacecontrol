# seriell einlesen ohne thread
# UNGETESTET: das wegwerfen von empfangenen zeilen, die mit ":" beginnen!

import logging

from flask import Flask, request, abort

from canbus import CanBus

logger = logging.getLogger(__name__)
app = Flask(__name__)

PORT = 8080

canbus = CanBus()

@app.route('/<client_name>/SetPort', methods=['POST'])
def set_port(client_name):
    try:
        port = int(request.args.get('port', -1))
    except TypeError:
        logger.error("invalid port")
        abort(400)
    try:
        state = int(request.args.get('state', -1))
    except TypeError:
        logger.error("invalid port state")
        abort(400)
    print port, state
    if port == -1 or state == -1:
        logger.error("invalid port or state")
        abort(400)
    client = canbus.get_can_client(client_name)
    return client.set_port(port, state)

@app.route('/<client_name>/GetAnalog', methods=['GET'])
def get_analog(client_name):
    try:
        port = int(request.args.get('port', -1))
    except TypeError:
        logger.error("invalid port")
        abort(400)
    if port == -1:
        logger.error("invalid port")
        abort(400)
    client = canbus.get_can_client(client_name)
    return client.get_analog(port)


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=PORT)
