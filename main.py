import json
import socket

HOST = "localhost"
PORT = 8800
HOURS = 24

SOLAR_LIMIT = 200.0
BATTERY_CAPACITY = 100.0
GENERATOR_COST = 1.0

INITIAL_BATTERY = 0.0

with socket.create_connection((HOST, PORT)) as sock:
    for hour in range(HOURS):
        message = sock.recv(4096) #4096 should be enough

        if not message:
            break

        data = json.loads(message.decode("utf-8"))

        event = data["random_event"] #random event
        forecast = data["forecast"] #forecast cloudy/not cloudy for NEXT hour
        price = data["grid_price"] #data grid price
        buildings = data["loads"] #type for types - load for loads
        