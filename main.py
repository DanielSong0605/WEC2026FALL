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
    
solar_left = SOLAR_LIMIT #kinda redundant i think but im stupid so idc
load = 0.0 
solerable_load = 0.0
demand = 0.0
#declaring all of these here for my own sake

if event == "cloudy_weather": 
    solar_left = 0.0 #no solar usable in cloudy weather

for building in buildings:
    demand = building["load"] 
    #for each building I have to check 
    #their required load so thats in demand

    if building["type"] == "lecture_hall":
        load += demand
    #lecture halls cant use solar anyway so their
    #demand goes straight into load
    else:
        solar = min(demand, solar_left)
    #solar here is the smaller number between demand and whatever
    #solar is left
        solerable_load += solar
        solar_left -= solar
        load += demand - solar
    #basically the solerable_load increases by the amount of load
    #solar is. Then solar_left loses that amount since theres max 200units
    #then load gets added whatever is left after demand - solar since if demand
    #is smaller than solar_left then its gonna be 0 but if demand is greater than
    #its gonna be whatever the remainder is
    #basically this loop tells us how much power is solarable and how much isnt 
            
        
