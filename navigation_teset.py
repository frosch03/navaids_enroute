# -*- coding: latin-1 -*-

import numpy as np
import xml.etree.ElementTree as ET
from itertools import chain

# N 48 32.8 E 008 56.7
# N 48 29.0 E 008 56.8
# N 48 28.6 E 008 44.1
# N 48 51.6 E 008 40.2
# N 48 51.8 E 009 13.5

def convToDegrees(old):
    direction = {'N':1, 'S':-1, 'E': 1, 'W':-1}
    new = old.replace('.',' ')
    new = new.split()
    return (int(new[1])+int(new[2])/60.0+int(new[3])/3600.0) * direction[new[0]]

tree = ET.parse('openaip_navaid_germany_de.aip')
root = tree.getroot()


def uniqFast(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if not (x in seen or seen_add(x))]

def getDistance(brgdst):
    return brgdst[2]

def getBearing(brgdst):
    return brgdst[1]

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
    r_m  = 6.371e6
    r_nm = 3443.92
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    dphi = np.radians(lat2-lat1)
    dlbd = np.radians(lon2-lon1)
    a = np.sin(dphi/2) * np.sin(dphi/2) + \
        np.cos(phi1)   * np.cos(phi2)   * \
        np.sin(dlbd/2) * np.sin(dlbd/2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    d = r_nm * c
    return d

def calcBrgDst(x, y):
    lat1 = float(x.find('GEOLOCATION/LAT').text)
    lon1 = float(x.find('GEOLOCATION/LON').text)
    lat2 = float(y.find('GEOLOCATION/LAT').text)
    lon2 = float(y.find('GEOLOCATION/LON').text)
    brng = bearing((lat1,lon1),(lat2,lon2))
    dist = distance((lat1,lon1),(lat2,lon2))
    return ((  x.find('ID').text + "->" + y.find('ID').text
             , int(brng)
             , int(dist)))


route_ = [ ("N 48 32.8","E 008 56.7")
         , ("N 48 29.0","E 008 56.8")
         , ("N 48 28.6","E 008 44.1")
         , ("N 48 51.6","E 008 40.2")
         , ("N 48 51.8","E 009 13.5")]
route  = map(lambda (x,y): (convToDegrees(x), convToDegrees(y)), route)

vors =   root[0].findall("./*[@TYPE='VOR']") \
       + root[0].findall("./*[@TYPE='DVOR']") \
       + root[0].findall("./*[@TYPE='DVOR-DME']") \
       + root[0].findall("./*[@TYPE='VORTAC']")

def bearingDistances2d(route):
    return map(lambda x: map(lambda y: calcBrgDst(x,y), vors), vors)

vor_bear_dists_2d = map(lambda x: map(lambda y: calcBrgDst(x,y), vors), vors)
vor_bear_dists    = list(chain.from_iterable(vor_distances_2d))

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
