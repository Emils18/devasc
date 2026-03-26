import requests
import urllib.parse
from datetime import datetime, timedelta

route_url = "https://graphhopper.com/api/1/route?"
key = "d229444b-25bc-418e-b3b9-faaca34a8dc9"

# --- Feature 1: Trip Cost / Energy Estimator ---
def calculate_trip_metrics(distance_km, vehicle):
    """
    Calculates cost for cars or calories for human-powered travel.
    Assumes average fuel efficiency: 8.5L / 100km
    Assumes average calorie burn: 50 kcal / km (walking) or 30 kcal / km (cycling)
    """
    if vehicle == "car":
        fuel_price = 1.50  # Average price per Liter
        liters_used = (distance_km / 100) * 8.5
        total_cost = liters_used * fuel_price
        return f"Estimated Fuel Cost: ${total_cost:.2f} (at $1.50/L)"
    
    elif vehicle == "foot":
        calories = distance_km * 50
        return f"Estimated Energy Burned: {calories:.0f} kcal"
    
    elif vehicle == "bike":
        calories = distance_km * 30
        return f"Estimated Energy Burned: {calories:.0f} kcal"
    
    return ""

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

        country = json_data["hits"][0]["country"] if "country" in json_data["hits"][0] else ""
        state = json_data["hits"][0]["state"] if "state" in json_data["hits"][0] else ""

        if len(state) != 0 and len(country) != 0:
            new_loc = name + ", " + state + ", " + country
        elif len(country) != 0:
            new_loc = name + ", " + country
        else:
            new_loc = name

        print("Geocoding API URL for " + new_loc +
              " (Location Type: " + value + ")\n" + url)

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

    vehicle = input("Enter a vehicle profile from the list above: ")

    if vehicle == "q" or vehicle == "quit":
        break

    elif vehicle not in profile:
        vehicle = "car"
        print("No valid vehicle profile was entered. Using the car profile.")

    loc1 = input("Starting Location: ")
    if loc1 == "quit" or loc1 == "q":
        break
    orig = geocoding(loc1, key)

    loc2 = input("Destination: ")
    if loc2 == "quit" or loc2 == "q":
        break
    dest = geocoding(loc2, key)

    print("=================================================")

    if orig[0] == 200 and dest[0] == 200:

        op = "&point=" + str(orig[1]) + "%2C" + str(orig[2])
        dp = "&point=" + str(dest[1]) + "%2C" + str(dest[2])

        paths_url = route_url + urllib.parse.urlencode({
            "key": key,
            "vehicle": vehicle
        }) + op + dp

        paths_status = requests.get(paths_url).status_code
        paths_data = requests.get(paths_url).json()

        print("Routing API Status:", paths_status)
        print("Routing API URL:\n", paths_url)

        print("=================================================")
        print("Directions from", orig[3], "to", dest[3], "by", vehicle)
        print("=================================================")

        if paths_status == 200:

            miles = (paths_data["paths"][0]["distance"]) / 1000 / 1.61
            km = (paths_data["paths"][0]["distance"]) / 1000

            # --- Feature 1: Trip Metrics ---
            metrics = calculate_trip_metrics(km, vehicle)
            print(metrics)

            # --- Feature 2: Arrival Time ---
            travel_time_ms = paths_data["paths"][0]["time"]
            current_time = datetime.now()
            arrival_time = current_time + timedelta(milliseconds=travel_time_ms)
            print(f"Current Time: {current_time.strftime('%I:%M %p')}")
            print(f"Estimated Arrival: {arrival_time.strftime('%I:%M %p')}")

            sec = int(travel_time_ms / 1000 % 60)
            min = int(travel_time_ms / 1000 / 60 % 60)
            hr = int(travel_time_ms / 1000 / 60 / 60)

            print("Distance Traveled: {0:.1f} miles / {1:.1f} km".format(miles, km))
            print("Trip Duration: {0:02d}:{1:02d}:{2:02d}".format(hr, min, sec))
            print("=================================================")

            for each in range(len(paths_data["paths"][0]["instructions"])):

                path = paths_data["paths"][0]["instructions"][each]["text"]
                distance = paths_data["paths"][0]["instructions"][each]["distance"]

                print("{0} ( {1:.1f} km / {2:.1f} miles )".format(
                    path,
                    distance / 1000,
                    distance / 1000 / 1.61
                ))

            print("=================================================")

        else:
            print("Error message:", paths_data.get("message", "Unknown error"))
            print("*************************************************")
