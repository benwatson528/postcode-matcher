import csv
from collections import Counter
from math import sin, cos, sqrt, atan2, radians
from pathlib import Path

import requests

# Approximate radius of earth in km
R = 6373
# The maximum number of postcodes that can be looked up at once
POSTCODES_IO_CHUNK_SIZE = 100
POSTCODES_IO_ENDPOINT = "http://api.postcodes.io/postcodes"
POSTCODES_IO_URL = "http://api.postcodes.io/postcodes"


def main():
    client_mappings = process_postcodes("clients")
    office_mappings = process_postcodes("offices")
    closest_offices = find_closest_office(client_mappings, office_mappings)
    write_output(closest_offices)


def process_postcodes(source):
    with open(f"input/{source}.csv") as f:
        postcodes = f.read().splitlines()
    return get_lat_longs(postcodes)


# Given a list of postcodes, returns a dict of postcode to the latitude and longitude (in radians). Postcodes for
# which no lat/longitude is found are removed
def get_lat_longs(postcodes):
    lat_longs = {}
    for chunk in [postcodes[i:i + POSTCODES_IO_CHUNK_SIZE] for i in range(0, len(postcodes), POSTCODES_IO_CHUNK_SIZE)]:
        response = requests.post(POSTCODES_IO_URL, data={"postcodes": chunk})
        response.raise_for_status()
        for result in response.json()["result"]:
            inner = result["result"]
            latitude, longitude = inner["latitude"], inner["longitude"]
            if latitude is not None and longitude is not None:
                lat_longs[inner["postcode"]] = (radians(latitude), radians(longitude))
    return lat_longs


# taken from https://stackoverflow.com/a/19412565/729819 - no external packages needed
def calculate_distance(lat1, lon1, lat2, lon2):
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def find_closest_office(client_mappings, office_mappings):
    closest_office_count = Counter()
    for (c_lat, c_lon) in client_mappings.values():
        min_distance = 9999999
        min_office = None
        for o_postcode, (o_lat, o_lon) in office_mappings.items():
            if (distance := calculate_distance(c_lat, c_lon, o_lat, o_lon)) < min_distance:
                min_distance = distance
                min_office = o_postcode
        closest_office_count[min_office] += 1
    return closest_office_count


def write_output(closest_offices):
    Path("output").mkdir(exist_ok=True)
    with open("output/results.csv", "w", newline='') as f:
        w = csv.writer(f)
        w.writerow(["office", "num_closest_clients"])
        w.writerows({k: v for k, v in sorted(closest_offices.items(), key=lambda item: item[1], reverse=True)}.items())


if __name__ == "__main__":
    main()
