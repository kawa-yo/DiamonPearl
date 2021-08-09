from __future__ import annotations
import numpy as np
from typing import List
from .meshdata import MeshCode
from . import R, rad2deg, deg2rad

class Point:
    def __init__( self,
                  latitude: float,   # <deg>
                  longitude: float,  # <deg>
                  elevation: float = None,  # <meter>
                  valid_elevation: float = None,  # <meter>
                  diameter: float = 0, #<meter>
                  name: str =None,
                  ) -> None:
        assert   0 <= latitude  and latitude  <  66
        assert 100 <= longitude and longitude < 180
        self.name = name
        self.latitude = latitude
        self.longitude = longitude 
        self.diameter = diameter

        self._mesh_code = MeshCode(latitude, longitude)
        self.elevation = elevation or self._mesh_code.elevation()
        self.valid_elevation = valid_elevation or self.elevation + .1
    
    def next( self,
              azimuth: float,  # [0,360]
              dist: float,  # <meter>
              valid_elevation: float,  #<meter>
              name: str = None,
              ) -> Point:
    
        a = dist / R
        b = np.pi / 2 - deg2rad(self.latitude)
        gamma = 2*np.pi - deg2rad(azimuth)
        c = np.arccos( np.cos(a) * np.cos(b) \
                     + np.sin(a) * np.sin(b) * np.cos(gamma) )
        alpha = np.arcsin( np.sin(a) * np.sin(gamma) / np.sin(c) )

        lat = rad2deg(np.pi / 2 - c)
        lon = self.longitude - rad2deg(alpha)
        return Point(lat, lon, valid_elevation=valid_elevation, name=name)
    
    def to_location_format(self) -> List[str, float, float]:
        return [
            self.name,
            self.latitude,
            self.longitude,
            self._mesh_code.label,
            self.elevation,
            self.valid_elevation,
            self.valid_elevation - self.elevation
            ]
    
    def __str__(self):
        return f"""
==== {self.name} ====
lat: {self.latitude}
log: {self.longitude}
  h: {self.elevation}
====================="""

def validElevation( dist: float, #<meter>
                    altitude: float, # [0,90]
                    root_point: Point,#<meter>
                    ) -> float:

    root_elevation = root_point.elevation \
                   + root_point.diameter * np.tan(deg2rad(altitude))

    theta = dist / R
    Y = deg2rad(90 - altitude)
    X = np.pi - Y - theta
    h1 = ( np.sin(Y) / np.sin(Y + theta) ) * (R + root_elevation) - R
    return h1