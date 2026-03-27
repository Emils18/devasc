import requests
import urllib.parse
from datetime import datetime, timedelta

route_url = "https://graphhopper.com/api/1/route?"
key = "d229444b-25bc-418e-b3b9-faaca34a8dc9"

# --- Feature 1: Trip Cost / Energy Estimator ---
def calculate_trip_metrics(distance_km, vehicle):
    if vehicle == "foot":
        calories = distance_km * 50
        return f"Estimated Energy Burned: {calories:.0f} kcal"
    
    elif vehicle == "bike":
        calories = distance_km * 30
        return f"Estimated Energy Burned: {calories:.0f} kcal"
    
    return ""

# --- Feature 4: Fuel Cost Calculator (User Input) ---
def calculate_fuel_cost(distance_km):
    try:
        fuel_price = float(input("Enter fuel price per liter: "))
        efficiency = float(input("Enter vehicle fuel efficiency (km per liter): "))
        
        liters_used = distance_km / efficiency
        total_cost = liters_used * fuel_price
        
        return f"Fuel Needed: {liters_used:.2f} L | Estimated Cost: ${total_cost:.2f}"
    
    except:
        return "Invalid fuel input."


def geocoding(location, key):

    while location == "":
        location = input("Enter location again: ")

    geocode_url = "https://graphhopper.com/api/1/geocode?"

    url = geocode_url + urllib.parse.urlencode({
        "q": location,
        "limit": "1",
        "key": key
    })

    replydata = requests.get(url)
    json_data = replydata.json()
    json_status = replydata.status_code

    if json_status == 200 and len(json_data["hits"]) != 0:

        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]

        name = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]

        country = json_data["hits"][0].get("country", "")
        state = json_data["hits"][0].get("state", "")

        if state and country:
            new_loc = f"{name}, {state}, {country}"
        elif country:
            new_loc = f"{name}, {country}"
        else:
            new_loc = name

        print("Geocoding API URL for " + new_loc +
              f" (Location Type: {value})\n{url}")

    else:
        lat = "null"
        lng = "null"
        new_loc = location

        if json_status != 200:
            print("Geocode API status:", json_status)
            print("Error message:", json_data.get("message", ""))

    return json_status, lat, lng, new_loc


while True:

    print("\n+++++++++++++++++++++++++++++++++++++++++++++")
    print("Vehicle profiles available on Graphhopper:")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    print("car, bike, foot")
    print("+++++++++++++++++++++++++++++++++++++++++++++")

    profile = ["car", "bike", "foot"]

    vehicle = input("Enter a vehicle profile: ")

    if vehicle in ["q", "quit"]:
        break

    elif vehicle not in profile:
        vehicle = "car"
        print("Invalid profile. Defaulting to car.")

    # --- Feature 3: Language Selection ---
    user_lang = input("Enter language code (en, es, fr, de): ") or "en"

    loc1 = input("Starting Location: ")
    if loc1 in ["q", "quit"]:
        break
    orig = geocoding(loc1, key)

    loc2 = input("Destination: ")
    if loc2 in ["q", "quit"]:
        break
    dest = geocoding(loc2, key)

    print("=================================================")

    if orig[0] == 200 and dest[0] == 200:

        op = "&point=" + str(orig[1]) + "%2C" + str(orig[2])
        dp = "&point=" + str(dest[1]) + "%2C" + str(dest[2])

        # --- Include language ---
        query_params = {
            "key": key,
            "vehicle": vehicle,
            "locale": user_lang
        }

        paths_url = route_url + urllib.parse.urlencode(query_params) + op + dp

        response = requests.get(paths_url)
        paths_status = response.status_code
        paths_data = response.json()

        print("Routing API Status:", paths_status)
        print("Routing API URL:\n", paths_url)

        print("=================================================")
        print("Directions from", orig[3], "to", dest[3], "by", vehicle)
        print("=================================================")

        if paths_status == 200:

            distance_m = paths_data["paths"][0]["distance"]
            km = distance_m / 1000
            miles = km / 1.61
            travel_time_ms = paths_data["paths"][0]["time"]

            # --- Feature 4 (car) OR Feature 1 (bike/foot) ---
            if vehicle == "car":
                print(calculate_fuel_cost(km))
            else:
                print(calculate_trip_metrics(km, vehicle))

            # --- Feature 2: Arrival Time ---
            current_time = datetime.now()
            arrival_time = current_time + timedelta(milliseconds=travel_time_ms)

            print(f"Current Time: {current_time.strftime('%I:%M %p')}")
            print(f"Estimated Arrival: {arrival_time.strftime('%I:%M %p')}")

            # Duration
            sec = int(travel_time_ms / 1000 % 60)
            min = int(travel_time_ms / 1000 / 60 % 60)
            hr = int(travel_time_ms / 1000 / 60 / 60)

            print("Distance: {0:.1f} km / {1:.1f} miles".format(km, miles))
            print("Duration: {0:02d}:{1:02d}:{2:02d}".format(hr, min, sec))

            print("=================================================")

            for instr in paths_data["paths"][0]["instructions"]:
                print(instr["text"])

            print("=================================================")

        else:
            print("Error:", paths_data.get("message", "Unknown error"))
