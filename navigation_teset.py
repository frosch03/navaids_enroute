#!/usr/bin/python
# -*- coding: latin-1 -*-

import sys
import numpy as np
import xml.etree.ElementTree as ET
from itertools import chain


def convToDegrees(old):
    direction = {'N': 1, 'S': -1, 'E': 1, 'W': -1}
    new = old.replace('.', ' ')
    new = new.split()
    return (int(new[1]) +
            int(new[2])/60.0 +
            int(new[3])/3600.0) * direction[new[0]]


def uniqFast(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def getDistance(brgdst):
    return brgdst[1][1]


def getBearing(brgdst):
    return brgdst[1][0]


def getFrequency(brgdst):
    return brgdst[0][1]


def getName(brgdst):
    return brgdst[0][0]


def sortDistance(brgdsts):
    return sorted(brgdsts, key=getDistance)


def sortBearing(brgdsts):
    return sorted(brgdsts, key=getBearing)


def bearing((lat1, lon1), (lat2, lon2)):
    return np.fmod((   360
                     + np.degrees(np.arctan2( np.sin(np.radians(lon2-lon1))*np.cos(np.radians(lat2))
                                            ,   (np.cos(np.radians(lat1))*np.sin(np.radians(lat2)))
                                              - (np.sin(np.radians(lat1))*np.cos(np.radians(lat2))*np.cos(np.radians(lon2-lon1))))))
                   , 360)


def distance((lat1, lon1), (lat2, lon2)):
    r_m = 6.371e6
    r_nm = 3443.92
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    dphi = np.radians(lat2-lat1)
    dlbd = np.radians(lon2-lon1)
    a = np.sin(dphi/2) * np.sin(dphi/2) + \
        np.cos(phi1) * np.cos(phi2) * \
        np.sin(dlbd/2) * np.sin(dlbd/2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    d = r_nm * c
    return d


def aipGetLatLon(navaid):
    lat = float(navaid.find('GEOLOCATION/LAT').text)
    lon = float(navaid.find('GEOLOCATION/LON').text)
    return (lat, lon)


def aipGetId(navaid):
    return (navaid.find('ID').text)


def calcBrgDst((lat1, lon1), (lat2, lon2)):
    brng = bearing((lat1, lon1), (lat2, lon2))
    dist = distance((lat1, lon1), (lat2, lon2))
    return (brng, dist)


def aipGetFrequency(navaid):
    return (float(navaid.find('RADIO/FREQUENCY').text))


def gpxGetLatLon(pt):
    lat = float(pt.attrib['lat'])
    lon = float(pt.attrib['lon'])
    return (lat, lon)


def gpxGetName(pt):
    return (pt.findall("{http://www.topografix.com/GPX/1/1}name")[0].text)


if len(sys.argv) <= 2:
    print "Usage:"
    print str(sys.argv[0]) + " <openaip navaid file> <.gpx route file>"
    exit()

# route_tree = ET.parse('route.gpx')
route_tree = ET.parse(sys.argv[2])
route_root = route_tree.getroot()
route_ = route_root[0].findall("{http://www.topografix.com/GPX/1/1}rtept")
route = map(lambda pt: (gpxGetName(pt), gpxGetLatLon(pt)), route_)

# navaids_tree = ET.parse('openaip_navaid_germany_de.aip')
navaids_tree = ET.parse(sys.argv[1])
navaids_root = navaids_tree.getroot()
vor_navaids = navaids_root[0].findall("./*[@TYPE='VOR']") \
              + navaids_root[0].findall("./*[@TYPE='DVOR']") \
              + navaids_root[0].findall("./*[@TYPE='DVOR-DME']") \
              + navaids_root[0].findall("./*[@TYPE='VORTAC']")
vors = map(lambda n: ((aipGetId(n), aipGetFrequency(n)), aipGetLatLon(n)), vor_navaids)

ndb_navaids = navaids_root[0].findall("./*[@TYPE='NDB']")
ndbs = map(lambda n: ((aipGetId(n), aipGetFrequency(n)), aipGetLatLon(n)), ndb_navaids)


def getNavaidsEnroute(navaids, route):
    return map(lambda (sr, r):
               map(lambda ((sn, fn), n):
                   ((sr + "->" + sn, fn), calcBrgDst(r, n)),
                   navaids),
               route)


def getNearestNavaidsEnroute(navaids, route, count=2):
    navaids_enroute = getNavaidsEnroute(navaids, route)
    return map(lambda naids:
               (uniqFast(sortDistance(naids)))[:count],
               navaids_enroute)


def showNavaidsEnroute(naids, route):
    for x in naids:
        for y in x:
            s = getName(y)
            b = str(int(getBearing(y)))
            d = str(round(getDistance(y), 2))
            f = "{:7.3f}".format(round(getFrequency(y), 3))
            print s + "(" + f + ")"": " + b + u"°, " + d + "NM"
        print "--"


showNavaidsEnroute(getNearestNavaidsEnroute(vors, route), route)

# <NAVAID TYPE="VOR">
#   <COUNTRY>DE</COUNTRY>
#   <NAME>BAYREUTH</NAME>
#   <ID>BAY</ID>
#   <GEOLOCATION>
#     <LAT>49.9866676331</LAT>
#     <LON>11.6383333206</LON>
#     <ELEV UNIT="M">487</ELEV>
#   </GEOLOCATION>
#   <RADIO>
#     <FREQUENCY>110.06</FREQUENCY>
#   </RADIO>
#   <PARAMS>
#     <DECLINATION>2.47592</DECLINATION>
#     <ALIGNEDTOTRUENORTH>FALSE</ALIGNEDTOTRUENORTH>
#   </PARAMS>
# </NAVAID>
