import requests
import urllib.parse

# API Key (replace with your own)
key = "d229444b-25bc-418e-b3b9-faaca34a8dc9"

route_url = "https://graphhopper.com/api/1/route?"

def geocoding(location, key):
    # Keep asking if input is empty
    while location.strip() == "":
        location = input("Enter the location again: ")

    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})

    try:
        replydata = requests.get(url)
        json_data = replydata.json()
        json_status = replydata.status_code
    except Exception as e:
        print(f"Error fetching data: {e}")
        return "null", "null", "null", location

    # Check for valid response and non-empty hits
    if json_status == 200 and len(json_data.get("hits", [])) != 0:
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]
        country = json_data["hits"][0].get("country", "")
        state = json_data["hits"][0].get("state", "")

        if state and country:
            new_loc = f"{name}, {state}, {country}"
        elif state:
            new_loc = f"{name}, {state}"
        elif country:
            new_loc = f"{name}, {country}"
        else:
            new_loc = name

        print(f"Geocoding API URL for {new_loc} (Location Type: {value})\n{url}")
        return json_status, lat, lng, new_loc
    else:
        print(f"Geocode API status: {json_status}")
        if "message" in json_data:
            print(f"Error message: {json_data['message']}")
        else:
            print("Error: Location not found.")
        return json_status, "null", "null", location

# Main program loop
while True:
    loc1 = input("Starting Location: ")
    if loc1.lower() in ["q", "quit"]:
        break
    orig = geocoding(loc1, key)
    print(orig)

    loc2 = input("Destination: ")
    if loc2.lower() in ["q", "quit"]:
        break
    dest = geocoding(loc2, key)
    print(dest)
