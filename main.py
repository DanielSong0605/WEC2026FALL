import json
import socket

HOST = "localhost"
PORT = 8800
HOURS = 24

SOLAR_LIMIT = 200
BATTERY_CAPACITY = 100
GENERATOR_COST = 1.0
battery_charge = 0
#this should be here not down there

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
        load = 0
        solarable_load = 0
        demand = 0
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
                solarable_load += solar
                solar_left -= solar
                load += demand - solar
            #basically the solarable_load increases by the amount of load
            #solar is. Then solar_left loses that amount since theres max 200units
            #then load gets added whatever is left after demand - solar since if demand
            #is smaller than solar_left then its gonna be 0 but if demand is greater than
            #its gonna be whatever the remainder is
            #basically this loop tells us how much power is solarable and how much isnt 
            
            #first algorithim iteration - charge battery to 100 on hour 1
            #then every time battery is used charge the amount used so its 100 always
            #just in case of grid failure
            #realistically only wasting 100 dollars? since paying for whta you use after
            #last round just use all battery
            
        battery_used = 0.0
        if event != "battery_failure":
            #obviously
            if (price > GENERATOR_COST or event == "grid_failure" or hour == HOURS - 1):
                #like above, if the grid cost is more than 1.0, gird failure is in play,
                #or its the 24 hour then use battery_charge
                battery_used = min(load, battery_charge)
                #either you use all the battery charge if load is greater or just enough to 
                #cover load
                
        grid_used = load - battery_used
        #grid_used is whatever the difference is if load is greater than the battery available
        #to use
        

        battery_charge -= battery_used
        #charge - the amount used
        
        generator = 0.0


        #this goes down here since charge happens the hour before
        #putting this above like i did earlier would be cheating
        if hour < HOURS - 1:
            #as long as its not the 23 hour
            if event != "generator_failure" and event != "battery_failure":
                #obviously
                generator = BATTERY_CAPACITY - battery_charge
                #generator produces whatever is needed to make battery full

        battery_charge += generator
        #battery charge + whatever the generator makes
        
        #boring json return part
        allocations = []
        solar_left = solarable_load
        battery_left = battery_used


        #retunr format is solar -> battery -> grid
        #so calculate in that order ig
        for building in buildings:
            #similar to loop above
            demand = building["load"]
            solar = 0.0

            if building["type"] != "lecture_hall":
                solar = min(demand, solar_left)
                solar_left -= solar
                #solar is either the demand or solar_left
                #so this gets how much of the building is solarable
                
            battery = min(demand - solar, battery_left)
            battery_left -= battery
            #gets how much of the buiilding is batteryable
            #0 if its all covered by solar
            #if no battery is left than its just 0 for battery_left so it goes to grid obv

            #if battery is all gone + solar
            #grid covers rest so
            grid = demand - solar - battery

            allocations.append({
                "solar": solar,
                "battery": battery,
                "grid": grid
            #add the building's stats to the list so its in the nice format
            })

        response = {
            #send back the list of buildings + stats
            "buildings": allocations,
            "generator": generator
            #and the generator used that hour
        }

        response_json = json.dumps(response)
        sock.sendall((response_json + "\n").encode("utf-8"))
        

