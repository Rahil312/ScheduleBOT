import os
import requests
import sys
import json

def get_key():
    '''
    Function to extract API key

    Returns
    -------
    api_key_1 : returns the API key for Google connection

    '''
    api_key_1 = ""
    key_data = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname
                                            (os.path.abspath(__file__)))), "json", "key.json")
    if not os.path.exists(key_data):
        print(
            '''API Key file does not exist. Please refer to README to add the key and restart the program.''')
        sys.exit("Thank you for using ScheduleBot")
    with open(key_data) as json_file:
        data = json.load(json_file)
        api_key_1 = data.get("key", "")
    return api_key_1

def get_lat_log(address, api_key_1):
    """
    Converts a textual address to a set of coordinates

    address : str
        The location for which coordinates are needed.

    Returns
    -------
    list or None
        The latitude and longitude of the given address using Google Maps, or None if not found.
    """
    if not api_key_1:
        print("No API key provided. Skipping location lookup.")
        return None

    address2 = address.replace(" ", "+")
    url = f"https://maps.googleapis.com/maps/api/geocode/json?key={api_key_1}&address={address2}&language=en-EN"
    try:
        r = requests.get(url)
        response_json = r.json()
        if response_json.get("results"):
            return [
                response_json["results"][0]["geometry"]["location"]["lat"],
                response_json["results"][0]["geometry"]["location"]["lng"]
            ]
        else:
            print(f"No results found for location: {address}")
            return None
    except (requests.RequestException, KeyError) as e:
        print(f"Error fetching coordinates for location '{address}': {e}")
        return None

def get_distance(dest, src, mode):
    """
    Gets the distance matrix which includes the travel time to the event

    dest : str
        Address of the event location.
    src : str
        Address of the source location.
    mode : str
        Mode of transportation.

    Returns
    -------
    tuple or None
        Travel time in seconds and a Google Maps link, or None if location not found.
    """
    api_key_1 = get_key()
    print(f"Source: {src}")
    print(f"Destination: {dest}")
    print(f"Mode: {mode}")

    dest_lat_lon = get_lat_log(dest, api_key_1)
    src_lat_lon = get_lat_log(src, api_key_1)

    if not dest_lat_lon or not src_lat_lon:
        print("One or both locations not found. Skipping distance calculation.")
        return None

    orig = f"{src_lat_lon[0]},{src_lat_lon[1]}"
    dest = f"{dest_lat_lon[0]},{dest_lat_lon[1]}"
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?key={api_key_1}&origins={orig}&destinations={dest}&mode={mode}&language=en-EN&sensor=false"
    
    try:
        r = requests.get(url)
        response_json = r.json()
        travel_time = response_json["rows"][0]["elements"][0].get("duration", {}).get("value")
        if travel_time is None:
            print("Duration not found in response. Skipping travel time calculation.")
            return None

        maps_link = f"https://www.google.com/maps/dir/?api=1&origin={orig}&destination={dest}&travelmode={mode.lower()}"
        print(f"Travel time: {travel_time} seconds")
        return travel_time, maps_link

    except (requests.RequestException, KeyError) as e:
        print(f"Error fetching travel time: {e}")
        return None
