import requests
import urllib.parse
from datetime import datetime, timedelta

route_url = "https://graphhopper.com/api/1/route?"
key = "d229444b-25bc-418e-b3b9-faaca34a8dc9"


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
            print("Error message:", json_data.get("message", "No message"))

    return json_status, lat, lng, new_loc


while True:

    print("\n+++++++++++++++++++++++++++++++++++++++++++++")
    print("Vehicle profiles available on Graphhopper:")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    print("car, bike, foot")
    print("+++++++++++++++++++++++++++++++++++++++++++++")

    profile = ["car", "bike", "foot"]
    vehicle = input("Enter a vehicle profile from the list above: ")

    if vehicle in ["q", "quit"]:
        break

    elif vehicle not in profile:
        vehicle = "car"
        print("No valid vehicle profile was entered. Using the car profile.")

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

        paths_url = route_url + urllib.parse.urlencode({
            "key": key,
            "vehicle": vehicle
        }) + op + dp

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
            miles = distance_m / 1000 / 1.61
            km = distance_m / 1000
            travel_time_ms = paths_data["paths"][0]["time"]

            sec = int(travel_time_ms / 1000 % 60)
            min = int(travel_time_ms / 1000 / 60 % 60)
            hr = int(travel_time_ms / 1000 / 60 / 60)

            print("Distance Traveled: {0:.1f} miles / {1:.1f} km".format(miles, km))
            print("Trip Duration: {0:02d}:{1:02d}:{2:02d}".format(hr, min, sec))

            # ----- Feature 1: Estimated Arrival Time -----
            current_time = datetime.now()
            arrival_time = current_time + timedelta(milliseconds=travel_time_ms)
            print(f"Current Time: {current_time.strftime('%I:%M %p')}")
            print(f"Estimated Arrival: {arrival_time.strftime('%I:%M %p')}")
            # --------------------------------------------

            print("=================================================")

            for instr in paths_data["paths"][0]["instructions"]:
                path = instr["text"]
                distance = instr["distance"]
                print("{0} ( {1:.1f} km / {2:.1f} miles )".format(
                    path,
                    distance / 1000,
                    distance / 1000 / 1.61
                ))

            print("=================================================")

        else:
            print("Error message:", paths_data.get("message", "No message"))
            print("*************************************************")
