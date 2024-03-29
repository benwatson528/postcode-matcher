# Postcode Matcher

Given a file containing client postcodes and a file containing office postcodes,
returns each base office and how many houses are closer to it than any other office.


## Running Instructions

1. Ensure Python 3 is installed (https://www.python.org/downloads/).
2. Download this application from GitHub https://github.com/benwatson528/postcode-matcher/archive/refs/heads/master.zip.
3. Unzip it and open the `postcode-matcher` folder.
4. Update `input/offices.csv` and `input/clients.csv`. These files should contain only postcodes, one per line. Sample files are included.
5. Run `main.py` with Python Launcher (it will be a right-click option on Mac).
The output will be written to `output/results.csv` as a CSV file with columns:

    1. `office` - the office postcode
    2. `num_closest` - the number of clients who are closer to this office than any other.

This file can be imported into Excel for further processing.


## Postcode Data

The lat/long for each postcode is found using the http://postcodes.io API, an open source project that is regularly
updated with the latest data from Ordnance Survey and the Office for National Statistics.

Postcodes for which no latitude/longitude is found are not included in the results.
