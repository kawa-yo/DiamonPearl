from __future__ import annotations
import numpy as np
import os
from urllib import parse, request
import json
from typing import List, Optional, Tuple
from meshdata import MeshCode

R = 6378.1 * 1000  # earth radius <meter>


class Point:
    def __init__( self,
                  latitude: float,   # <deg>
                  longitude: float,  # <deg>
                  valid_height: float = None,  # <meter>
                  name: str =None,
                  ) -> None:
        assert   0 <= latitude  and latitude  <  66
        assert 100 <= longitude and longitude < 180
        self.name = name
        self.latitude = latitude
        self.longitude = longitude 

        self._mesh_code = MeshCode(latitude, longitude)
        self.height = self._mesh_code.height()
        self.valid_height = valid_height if valid_height is not None else self.height + .1
    
    def next( self,
              azimuth: float,  # 0-2pi
              dist: float,  # <meter>
              valid_height: float = None,  #<0-pi/2>
              name: str = None,
              ) -> Point:
    
        a = dist / R
        b = np.pi / 2 - deg2rad(self.latitude)
        gamma = 2*np.pi - azimuth
        c = np.arcsin( np.sqrt(1 - ( np.sin(a) * np.sin(b) * np.cos(gamma) \
                                   + np.cos(a) * np.cos(b) \
                                    )**2) )
        alpha = np.arcsin( np.sin(a) * np.sin(gamma) / np.sin(c) )

        lat = rad2deg(np.pi / 2 - c)
        lon = self.longitude - rad2deg(alpha)
        return Point(lat, lon, valid_height, name=name)
    
    def to_location_format(self) -> List[str, float, float]:
        return [
            self.name,
            self.latitude,
            self.longitude,
            self._mesh_code.label,
            self.height,
            self.valid_height,
            self.valid_height - self.height
            ]
    
    def __str__(self):
        return f"""
==== {self.name} ====
lat: {self.latitude}
log: {self.longitude}
  h: {self.height}
====================="""

def validHeight( dist: float, #<meter>
                 altitude: float, # [0,90]
                 root_height: float #<meter>
                 ) -> float:
    theta = dist / R
    Y = deg2rad(90 - altitude)
    X = np.pi - Y - theta
    h1 = ( np.sin(Y) / np.sin(Y + theta) ) * (R + root_height) - R
    return h1

def isViewable( point: Point,
                prev: Point,
                dist: float,  #<meter>
                lower_limit: float = 1000,  #<meter>
                upper_limit: float = 20000, #<meter>
                ) -> bool:
    flag = point.height > point.valid_height \
        and prev.height <= prev.valid_height
    flag &= (lower_limit <= dist and dist <= upper_limit )
    return flag

def sun_rise_set( point: Point,
                  date_str: str,  # YYYY/MM/DD
                  verbose: bool = False,
             ) -> Tuple[int, int]:  # (rise_hour, rise_min, set_hour, set_min) 
    date = [int(d) for d in date_str.split("/")]
    assert len(date) == 3

    url = "https://mgpn.org/api/sun/position.cgi?json&"
    param = parse.urlencode({
        "y": date[0],
        "m": date[1],
        "d": date[2],
        "h": 5,
        "lat": point.latitude,
        "lon": point.longitude 
    })
    req = request.urlopen(url + param).read()
    res = json.loads(req.decode("utf-8"))
    rise = res["result"]["sunrise"][-5:]
    rise_hour = int(rise[:2])
    rise_min  = int(rise[-2:])
    set = res["result"]["sunset"][-5:]
    set_hour = int(set[:2])
    set_min  = int(set[-2:])
    if verbose:
        print(f"sunrise: {rise} / sunset: {set}")
    return rise_hour, rise_min, set_hour, set_min

def deg2rad(deg: float) -> float:
    return np.pi * deg / 180

def rad2deg(rad: float) -> float:
    return rad * 180 / np.pi

if __name__ == "__main__":
    fuji = Point(35.3606, 138.7274, name="Mt.Fuji")
    date = "2021/7/10"
    sun_rise_set(fuji, date)