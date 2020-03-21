'''
parse country case counts provided by OurWorldInData and write results to json
this should be run from the top level of the repo.

Will need to be integrated with other parsers once they become available.
'''
import csv
from io import StringIO
from urllib.request import urlopen
from collections import defaultdict
from datetime import datetime
from utils import write_tsv

# -----------------------------------------------------------------------------
# Globals

URL  = "https://covid.ourworldindata.org/data/full_data.csv"
LOC  = 'case-counts'
cols = ['location', 'time', 'cases', 'deaths', 'hospitalized', 'ICU', 'recovered']

# -----------------------------------------------------------------------------
# Functions

def sorted_date(s):
    return sorted(s, key=lambda d: datetime.strptime(d["time"], "%Y-%m-%d"))

def stoi(x):
    if x == "":
        return 0

    return int(x)

def retrieve_case_data():
    cases = defaultdict(list)
    with urlopen(URL) as res:
        buf = StringIO(res.read().decode(res.headers.get_content_charset()))
        crd = csv.reader(buf)

        Ix = {elt : i for i, elt in enumerate(next(crd))}
        for row in crd:
            country, date = row[Ix['location']], row[Ix['date']]
            cases[country].append({"time": date, "deaths": stoi(row[Ix['total_deaths']]), "cases":  stoi(row[Ix['total_cases']])})

        for cntry, data in cases.items():
            cases[cntry] = sorted_date(cases[cntry])

    return dict(cases)

def flatten(cases):
    rows = []
    for cntry, data in cases.items():
        for datum in data:
            rows.append([cntry, datum['time'], datum['cases'], datum['deaths'], None, None, None])

    return rows

# -----------------------------------------------------------------------------
# Main point of entry

def parse():
    cases = retrieve_case_data()
    cases = flatten(cases)

    write_tsv(f"{LOC}/World.tsv", cols, cases, "world")
