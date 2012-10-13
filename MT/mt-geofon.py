#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------
# Filename: mt-geofon.py
#  Purpose: Downloads all moment tensor solutions from GEOFON
#           Global Seismic Monitor
#           http://geofon.gfz-potsdam.de/eqinfo/list.php
#   Author: Robert Barsch
#    Email: barsch@lmu.de
#  License: GPLv2
#
# Copyright (C) 2011 Robert Barsch
#---------------------------------------------------------------------

from obspy.core import UTCDateTime
from optparse import OptionParser
import os
import re
import urllib
import glob


CATALOG_URL = "http://geofon.gfz-potsdam.de/eqinfo/list.php?%s"
ALERT_URL = "http://geofon.gfz-potsdam.de/geofon/alerts/"
PATTERN = ALERT_URL + r"\w+/mt.txt"
DEFAULT_DIR = 'data'


def fetch(datemin=UTCDateTime(2011, 1, 1), datemax=UTCDateTime(), latmin= -90,
          latmax=90, lonmin= -180, lonmax=180, magmin=0, nmax=999999,
          datadir='mt-geofon'):
    """
    Downloads all moment tensor solutions from GEOFON Global Seismic Monitor.

    :param datemin: string, optional
        Start date - MT catalog starts 01/2011 - so dates before will be
        truncated to 2011-01-01, defaults to '2011-01-01'.
    :param datemax: string, optional
        End date, defaults to today.
    :param latmin: float, optional
        Latitude minimum, defaults to -90.
    :param latmax: float, optional
        Latitude maximum, defaults to 90.
    :param lonmin: float, optional
        Longitude minimum, defaults to -180.
    :param lonmax: float, optional
        Longitude maximum, defaults to 180.
    :param magmin: float, optional
        Magnitude minimum, defaults to 0.
    :param nmax: int, optional
        Max entries, defaults to 999999.
    :param datadir: string, optional
        Directory where moment tensors are saved into, defaults to 'mt-geofon'.
    """
    # process input parameters
    datemin = UTCDateTime(datemin)
    if datemin < UTCDateTime(2011, 1, 1):
        datemin = UTCDateTime(2011, 1, 1)
    datemin = datemin.date
    datemax = UTCDateTime(datemax).date
    params = urllib.urlencode({'fmt': 'html',
                               'datemin': datemin, 'datemax': datemax,
                               'latmin': latmin, 'latmax': latmax,
                               'lonmin': lonmin, 'lonmax': lonmax,
                               'magmin': magmin, 'nmax': nmax})
    # fetch catalog
    data = urllib.urlopen(CATALOG_URL % params).read()
    # filter for moment tensors
    urls = re.findall(PATTERN, data)
    print "Found %d moment tensors" % len(urls)
    # save moment tensor files into given directory
    if not os.path.exists(datadir):
        os.mkdir(datadir)
    for url in urls:
        print "Fetching %s ..." % url
        data = urllib.urlopen(url).read()
        dt = data.splitlines()[1].replace(' ', '_').replace('/', '-')
        filename = os.path.join(datadir, '20' + dt + '.txt')
        fh = open(filename, 'wt')
        fh.write(data)
        fh.close()


def parse(datadir='data'):
    """
    Parses all downloaded moment tensor solution files.

    >>> data = parse()
    >>> data.values()[0]
    {'mtt': -3.8e+16, 'mrt': -3.8e+16, 'region': 'Solomon Islands',
     'no_of_stations': 38, 'mrp': 9.4e+16, 'magnitude_unit': 'MW',
     'longitude': 157.189, 'depth': 10, 'magnitude': 5.6, 'mrr': 9.4e+16,
     'mpp': 9.4e+16, 'latitude': -8.963,
     'dt': UTCDateTime(2011, 3, 4, 4, 7, 56, 930000), 'mtp': -3.8e+16}
    """
    pattern = os.path.join(datadir, '*.txt')
    files = glob.glob(pattern)
    results = {}
    for file in files:
        try:
            data = open(file, 'rt').read().splitlines()
            # check for format specific keyword
            if 'Centroid' in data[8]:
                o = 2
            else:
                o = 0
            dt = UTCDateTime('20' + data[1].replace('/', '-'))
            temp = {}
            temp['dt'] = dt
            temp['id'] = data[0]
            temp['url'] = ALERT_URL + data[0].split()[-1] + '/mt.txt'
            temp['region'] = data[2]
            temp['magnitude'] = float(data[4].split()[1])
            temp['magnitude_unit'] = data[4].split()[0]
            temp['latitude'] = float(data[3].split()[1])
            temp['longitude'] = float(data[3].split()[2])
            temp['depth'] = int(data[7 + o].split()[1])
            temp['no_of_stations'] = int(data[7 + o].split()[-1])
            sc = pow(10, int(data[8 + o].split('**')[-1].split()[0]))
            temp['mrr'] = float(data[9 + o].replace('=', ' ').split()[1]) * sc
            temp['mtt'] = float(data[9 + o].replace('=', ' ').split()[3]) * sc
            temp['mpp'] = float(data[9 + o].replace('=', ' ').split()[1]) * sc
            temp['mrt'] = float(data[9 + o].replace('=', ' ').split()[3]) * sc
            temp['mrp'] = float(data[9 + o].replace('=', ' ').split()[1]) * sc
            temp['mtp'] = float(data[9 + o].replace('=', ' ').split()[3]) * sc
        except Exception, e:
            print "Format error in %s: %s" % (file, str(e))
            continue
        results[dt] = temp
    return results


def main():
    usage = "Usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-d", default='mt-geofon', type="string", dest="datadir",
        help="Directory for moment tensor files, defaults to 'mt-geofon'.")
    parser.add_option("-s", "--datemin", default='2011-01-01', type="string",
        dest="datemin", help="Start date, defaults to '2011-01-01'.")
    parser.add_option("-e" , "--datemax", default=str(UTCDateTime().date),
        type="string", dest="datemax", help="End date, defaults to today.")
    parser.add_option("-m", "--magmin", default=0, type="float", dest="magmin",
        help="Minimal magnitude, defaults to 0.")
    parser.add_option("-n", "--nmax", default=999999, type="int", dest="nmax",
        help="Max entries, defaults to 999999.")
    parser.add_option("--latmin", default= -90, type="float", dest="latmin",
        help="Latitude minimum, defaults to -90.")
    parser.add_option("--latmax", default=90, type="float", dest="latmax",
        help="Latitude maximum, defaults to 90.")
    parser.add_option("--lonmin", default= -180, type="float", dest="lonmin",
        help="Longitude minimum, defaults to -180.")
    parser.add_option("--lonmax", default=180, type="float", dest="lonmax",
        help="Longitude maximum, defaults to 180.")
    (options, args) = parser.parse_args()
    fetch(**options.__dict__)


if __name__ == "__main__":
    main()
