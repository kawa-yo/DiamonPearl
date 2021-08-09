from __future__ import annotations
from urllib import parse, request
import json
from typing import Tuple, Dict
import ephem
import datetime as dt
import pytz
import math
from .point import Point

BODY = {
    "SUN": ephem.Sun(),
    "MOON": ephem.Moon(),
}

def _sun_rise_set( point: Point,
                   date: dt.date,
                   verbose: bool = False,
                   ) -> Tuple[int, int]:  # (rise_hour, rise_min, set_hour, set_min) 
    url = "https://mgpn.org/api/sun/position.cgi?json&"
    param = parse.urlencode({
        "y": date.year,
        "m": date.month,
        "d": date.day,
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

def rise_set( astbody: str,
              point: Point,
              date: dt.date,
              ) -> Tuple[dt.datetime, dt.datetime]:
    assert astbody in BODY
    datetime = dt.datetime.combine( date, dt.time(0, 0) )
    obs = Observer( point, datetime )
    body = BODY[astbody]
    body.compute(obs)
    rise = ephem.localtime( obs.next_rising(body))
    set  = ephem.localtime( obs.next_setting(body))
    return rise, set

def Observer( point: Point,
              date_time: dt.datetime,
              ) -> ephem.Observer:
    obs = ephem.Observer()
    obs.lat = str(point.latitude)
    obs.lon = str(point.longitude)
    obs.elevation = point.elevation
    obs.date = date_time.astimezone(pytz.utc)
    return obs

def sun_direction( point: Point,
                   datetime: dt.datetime,
                   method: str = "ephem",
                   ) -> Tuple[float, float]:

    assert method in ["ephem", "api"]

    if method == "api":
        return _sun_direction_api( point, datetime )

    return _sun_direction_ephem( point, datetime )

def _sun_direction_api( point: Point,
                        datetime: dt.datetime,
                        ) -> Tuple[float, float]:

    url = "https://mgpn.org/api/sun/position.cgi?json&"
    param = parse.urlencode({
        "y": datetime.year,
        "m": datetime.month,
        "d": datetime.day,
        "h": datetime.hour,
        "min": datetime.minute,
        "lat": point.latitude,
        "lon": point.longitude 
    })
    req = request.urlopen(url + param).read()
    res = json.loads(req.decode("utf-8"))
    return float(res["result"]["altitude"]), float(res["result"]["azimuth"])

def _sun_direction_ephem( point: Point,
                          datetime: dt.datetime,
                          ) -> Tuple[float, float]:
    observer = Observer( point, datetime )
    sun = ephem.Sun()
    sun.compute(observer)
    return math.degrees(sun.alt), math.degrees(sun.az)

if __name__ == "__main__":
    fuji = Point( 35.362797, 138.730878, elevation=3776, name="Mt_Fuji")
    ymnk = Point( 35.421686, 138.883249, elevation= 985, name="Lake_Yamanaka")
    datetime = dt.datetime(2021, 8, 20, 0, 0)
    obs = Observer( ymnk, datetime )
    sun = ephem.Moon()
    sun.compute(obs)
    print(sun.__bases__)
    print(ephem.localtime( obs.next_rising(sun)), ephem.localtime( obs.next_setting(sun)))
    
