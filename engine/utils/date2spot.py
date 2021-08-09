import numpy as np
from typing import List, Optional
import datetime as dt
from . import R, deg2rad, rad2deg
from .exceptions import AltitudeError, SpotNotFoundException
from .point import Point, validElevation
from .compass import rise_set, sun_direction
from .meshdata import FILE_NOT_EXIST_ELEVATION, UNEXIST

ELEVATION_TOLERANCE = 10

def find_all_spots( root_point: Point,
                    date: dt.date,  # YYYY/MM/DD
                    min_interval: int=20,
                    dist_interval: int=100,
                    ) -> List[Point,]:

    rise, set = rise_set( "SUN", root_point, date )
    rise = rise.hour*60 + rise.minute 
    rise = (rise // min_interval + 1) * (min_interval)  # minimum divisor of `min_interval` greater than original `rise` 
    set = set.hour*60 + set.minute 
    set = (set // min_interval) * (min_interval)  # maximum divisor of `min_interval` smaller than original `set` 

    print(rise, set)
    time = rise
    points = [root_point]
    for phase in ["rise", "set"]:
        if phase == "rise":
            RANGE = range(rise, 12*60, min_interval)
        else:
            RANGE = range(set, 12*60, -min_interval)
        for time in RANGE:
            hour, min = time//60, time%60
            datetime = dt.datetime.combine( date, dt.time(hour, min) )
            try:
                point = find_spot( root_point, datetime, interval=dist_interval )
                points.append(point)
            except AltitudeError as e:
                print(e)
                break
            except SpotNotFoundException as e:
                print(e)
                continue
    return points


def find_spot( root_point: Point,
               datetime: dt.datetime,  # YYYY/MM/DD/hh/mm
               start: int =   1000, #<meter>
               end:   int = 150000, #<meter>
               interval: int = 100,  #<meter>
               ) -> Point:

    altitude, azimuth = sun_direction( root_point, datetime, "ephem")
    azimuth += 180
    print(datetime)

    if not AltitudeError.isValid(altitude):
        raise AltitudeError(altitude)
    
    for dist in range(start, end, interval):
        velev = validElevation(dist, altitude, root_point)
        try:
            next = root_point.next(azimuth, dist, velev, name="{:02d}:{:02d}".format(
                datetime.hour, datetime.minute
            ))
            if next.elevation == FILE_NOT_EXIST_ELEVATION:
                continue

            dE = next.elevation - next.valid_elevation
            if dE >= 0 and interval <= 10 and dE < ELEVATION_TOLERANCE:
                return next
            elif dE >= 0 and interval <= 10:
                break
            elif dE >= 0:
                return find_spot( root_point, datetime, dist-interval, dist, max(10, interval//10) )

        except FileNotFoundError as e:
            mc = next._mesh_code
            about = mc.primary*100 + mc.secondary
            print(e)
            break

    raise SpotNotFoundException(datetime, azimuth, altitude)

def isViewable( point: Point,
                tolerance: float = 10,  #<meter>
                ) -> bool:
    delta = point.elevation - point.valid_elevation
    return 0 <= delta and delta < tolerance