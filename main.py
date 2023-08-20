import csv
import pathlib
import subprocess
import sys
from collections import Counter
from pathlib import Path

subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "geopy"])

import requests
from geopy.distance import geodesic

# Approximate radius of earth in km
R = 6373
# The maximum number of postcodes that can be looked up at once
POSTCODES_IO_CHUNK_SIZE = 100
POSTCODES_IO_URL = "http://api.postcodes.io/postcodes"


def main():
    client_mappings = process_postcodes("clients")
    office_mappings = process_postcodes("offices")
    closest_offices = find_closest_office(client_mappings, office_mappings)
    write_output(closest_offices)


def process_postcodes(source):
    with open(f"{pathlib.Path(__file__).parent}/input/{source}.csv") as f:
        postcodes = f.read().splitlines()
    return get_lat_longs(postcodes)


# Given a list of postcodes, returns a dict of postcode to the latitude and longitude. Postcodes for which no
# lat/longitude is found are removed
def get_lat_longs(postcodes):
    lat_longs = {}
    for chunk in [postcodes[i:i + POSTCODES_IO_CHUNK_SIZE] for i in range(0, len(postcodes), POSTCODES_IO_CHUNK_SIZE)]:
        response = requests.post(POSTCODES_IO_URL, data={"postcodes": chunk})
        response.raise_for_status()
        for result in response.json()["result"]:
            inner = result["result"]
            if not inner:
                print(f"Unable to find information about postcode {result['query']}")
            else:
                latitude, longitude = inner["latitude"], inner["longitude"]
                if latitude is not None and longitude is not None:
                    lat_longs[inner["postcode"]] = (latitude, longitude)
    return lat_longs


def find_closest_office(client_mappings, office_mappings):
    closest_office_count = Counter()
    for c_coords in client_mappings.values():
        min_distance = 9999999
        min_office = None
        for o_postcode, o_coords in office_mappings.items():
            if (distance := geodesic(c_coords, o_coords)) < min_distance:
                min_distance = distance
                min_office = o_postcode
        closest_office_count[min_office] += 1
    return closest_office_count


def write_output(closest_offices):
    Path(f"{pathlib.Path(__file__).parent}/output").mkdir(exist_ok=True)
    with open(f"{pathlib.Path(__file__).parent}/output/results.csv", "w", newline='') as f:
        w = csv.writer(f)
        w.writerow(["office", "num_closest_clients"])
        w.writerows({k: v for k, v in sorted(closest_offices.items(), key=lambda item: item[1], reverse=True)}.items())


if __name__ == "__main__":
    main()
