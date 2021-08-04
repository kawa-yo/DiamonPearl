import flask
from flask import Flask, render_template, abort
import numpy as np
import pandas as pd
from typing import List, Optional
from urllib import parse, request
import traceback
import json
from utils import Point, isViewable, validHeight, deg2rad, sun_rise_set
from exceptions import AltitudeError, SpotNotFoundException


app = Flask(__name__)
df = pd.read_csv("resource/data.csv")

@app.route("/")
def home():
    return render_template("home.html", title="dp_home")

@app.route("/REQ", methods=["GET", "POST"])
def req():
    try:
        if flask.request.method == 'GET':
            return flask.request.args.get('landmark', '')
        elif flask.request.method == 'POST':
            # landmark=flask.request.form["landmark"]
            # row = df[df["name"] == landmark].iloc[0]
            fuji = Point(35.3606, 138.7274, name="Mt.Fuji")
            _spots = find_all_spots( fuji, "2021/10/1", min_interval=10 )
            locations = [s.to_location_format() for s in _spots]
            return render_template( "mappage.html",
                                    title="map page",
                                    landmark=fuji.name,
                                    latitude=fuji.latitude,
                                    longitude=fuji.longitude,
                                    height=fuji.height,
                                    locations=locations
                                    )
        else:
            return abort(400)
    except Exception as e:
        traceback.print_exc()
        return str(e)

def find_all_spots( root_point: Point,
                    date_str: str,  # YYYY/MM/DD
                    min_interval: int=20,
                    dist_interval: int=100,
                    ) -> List[Point,]:

    date = [int(d) for d in date_str.split("/")]
    assert len(date) == 3
    _rise_h, _rise_m, _set_h, _set_m = sun_rise_set( root_point, date_str, True )
    rise = _rise_h*60 + _rise_m
    rise = (rise // min_interval + 1) * (min_interval)  # minimum divisor of `min_interval` greater than original `rise` 
    set = _set_h*60 + _set_m
    set = (set // min_interval) * (min_interval)  # maximum divisor of `min_interval` smaller than original `set` 

    print(rise, set)
    time = rise
    iter = (set - rise) // min_interval
    points = [root_point]
    for phase in ["rise", "set"]:
        if phase == "rise":
            RANGE = range(rise, 12*60, min_interval)
        else:
            RANGE = range(set, 12*60, -min_interval)
        for time in RANGE:
            hour, min = time//60, time%60
            hour = hour % 24
            date_time_str = f"{date_str}/{hour}/{min}"
            print(date_time_str)
            try:
                point = find_spot( root_point, date_time_str, interval=dist_interval )
                points.append(point)
            except AltitudeError as e:
                print(e)
                break
            except SpotNotFoundException as e:
                print(e)
                continue
    return points


def find_spot( root_point: Point,
               date_time_str: str,  # YYYY/MM/DD/hh/mm
               start: int = 0, #<meter>
               end:   int = 50000, #<meter>
               interval: int = 100,  #<meter>
               ) -> Point:
    date = [int(t) for t in date_time_str.split("/")]
    assert len(date) == 5
    url = "https://mgpn.org/api/sun/position.cgi?json&"
    param = parse.urlencode({
        "y": date[0],
        "m": date[1],
        "d": date[2],
        "h": date[3],
        "min": date[4],
        "lat": root_point.latitude,
        "lon": root_point.longitude 
    })
    req = request.urlopen(url + param).read()
    res = json.loads(req.decode("utf-8"))
    azimuth = deg2rad(float(res["result"]["azimuth"])) + np.pi
    altitude = float(res["result"]["altitude"]) 

    if not AltitudeError.isValid(altitude):
        raise AltitudeError(altitude)

    prev = root_point
    for dist in range(start, end, interval):
        vheight = validHeight(dist, altitude, root_point.height)
        try:
            next = root_point.next(azimuth, dist, vheight, name="{:02d}:{:02d}".format(date[3], date[4]))
            if isViewable( next, prev, dist ):
                if interval <= 10:
                    return next
                else:
                    return find_spot( root_point, date_time_str, dist-interval, dist, max(10, interval//10) )
        except FileNotFoundError as e:
            print(e)
            break

    raise SpotNotFoundException(date_time_str, azimuth, altitude)


if __name__ == "__main__":
    # fuji = Point(35.3606, 138.7274, name="Mt.Fuji")
    # date_str = "2021/7/10"
    # points = find_all_spots(fuji, date_str)
    # for p in points:
    #     print(p)
    app.run(debug=True)
