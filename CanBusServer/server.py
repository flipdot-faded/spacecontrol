# seriell einlesen ohne thread
# UNGETESTET: das wegwerfen von empfangenen zeilen, die mit ":" beginnen!

import logging
import struct

from flask import Flask, request, abort

from canbus import CanBus

logger = logging.getLogger(__name__)
app = Flask(__name__)

PORT = 8080

canbus = CanBus()

@app.route('/<client_name>/SetPort', methods=['POST'])
def set_port(client_name):
    try:
        port = int(request.args.get('port', None))
    except TypeError:
        logger.error("invalid port")
        abort(400)
    try:
        state = int(request.args.get('state', None))
    except TypeError:
        logger.error("invalid port state")
        abort(400)
    client = canbus.get_can_client(client_name)
    return client.set_port(port, state)

@app.route('/<client_name>/SetServo', methods=['POST'])
def set_port(client_name):
    try:
        servo_id = int(request.args.get('id', None))
    except TypeError:
        logger.error("invalid servo id")
        abort(400)
    try:
        servo_angle = int(request.args.get('angle', None))
    except TypeError:
        logger.error("invalid angle")
        abort(400)
    client = canbus.get_can_client(client_name)
    return client.set_port(servo_id, servo_angle)

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

@app.route('/<client_name>/GetPort', methods=['GET'])
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
    return client.get_port(port)

@app.route('/<client_name>/GetTemperature', methods=['GET'])
def get_analog(client_name):
    client = canbus.get_can_client(client_name)
    return client.get_temp()

@app.route('/<client_name>/SetRgb', methods=['POST'])
def set_rgb(client_name):
    try:
        r = int(request.args.get('R', -1))
        g = int(request.args.get('G', -1))
        b = int(request.args.get('B', -1))
    except TypeError:
        hexstr = request.args.get('hex', None)
        if not hexstr:
            logger.error("invalid RGB")
            abort(400)
        # TODO: may require some try / except clause
        rgb_data = hexstr.decode('hex')
        r, g, b = struct.unpack('BBB', rgb_data)
    client = canbus.get_can_client(client_name)
    return client.set_rgb(r, g, b)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
