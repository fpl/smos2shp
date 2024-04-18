#!/usr/bin/env python

import glob
import sys
import fiona
from fiona.crs import from_epsg
from netCDF4 import Dataset

def convert(target, outshp):
    pts = {}
    for i, nc in enumerate(target):
        sys.stderr.write("({} of {}) - Reading {}\n".format(i+1, len(target), nc))
        sm = Dataset(nc)
        lats = sm.variables['lat']
        longs = sm.variables['lon']
        data = sm.variables['Soil_Moisture']
        for i in range(len(lats)):
            for j in range(len(longs)):
                if data[i][j]: pts[(lats[i], longs[j])] = data[i][j]

    sys.stderr.write("Converting to shapefile\n")

    # Open a collection for writing.
    with fiona.open(
            outshp, 'w',
            crs=from_epsg(4326),
            driver='ESRI Shapefile',
            schema={
                'geometry': 'Point',
                'properties': {
                'soil_moist': 'float'}}
            ) as dest:

        for (lon, lat), moist in pts.items():
            geom = {
                'type': "Point",
                'coordinates': [lon, lat]}
            feature = {
                'type': "Feature",
                'geometry': geom,
                'properties': {
                'soil_moist': moist}}
            dest.write(feature)


if __name__ == "__main__":
    ncs = glob.glob(sys.argv[1] + ".nc")
    outshp = sys.argv[2] + ".shp"
    convert(ncs, outshp)
