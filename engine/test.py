from urllib import parse, request
from utils import Point, deg2rad, validHeight
import numpy as np
import matplotlib.pyplot as plt
import json
import traceback
from typing import List, Optional
from main import find_spot

def sec2deg(deg, min, sec):
    return deg + (min + sec / 60.) / 60.

def getHeight():
    fuji = Point("Mt.Fuji", 35.3606, 138.7274)
    url = "https://cyberjapandata2.gsi.go.jp/general/dem/scripts/getelevation.php?"
    param = parse.urlencode({
        "lon": fuji.longitude,
        "lat": fuji.latitude
    })
    f_url = request.urlopen(url + param).read()
    result = json.loads(f_url.decode("utf-8"))
    fuji.height = result["elevation"]
    print(fuji)


def sun():
    fuji = Point("Mt.Fuji", 35.3606, 138.7274)
    url = "https://mgpn.org/api/sun/position.cgi?json&"
    param = parse.urlencode({
        "y": 2021,
        "m": 7,
        "d": 10,
        "h": 5,
        "min": 00,
        "lat": fuji.latitude,
        "lon": fuji.longitude 
    })
    print(url + param)
    req = request.urlopen(url + param).read()
    res = json.loads(req.decode("utf-8"))
    print(res)

# not work
def geo_location():
    url = "https://ucopendb.gsi.go.jp/ucode/api/search.json?"
    param = parse.urlencode({
        "name": "富士山",
        "feature": "山頂",
        "pref_code": 22
    })
    req = request.urlopen(url + param).read()
    res = json.loads(req.decode("utf-8"))
    print(res)


def some_points( interval: int,  #<meter>
                 limit: int,  # num of point
                 date_str: str,  # YYYY/MM/DD/hh/mm
                 ) -> List[Point,]:
    fuji = Point(35.3606, 138.7274, name="Mt.Fuji")
    date = [int(t) for t in date_str.split("/")]
    assert len(date) == 5
    url = "https://mgpn.org/api/sun/position.cgi?json&"
    param = parse.urlencode({
        "y": date[0],
        "m": date[1],
        "d": date[2],
        "h": date[3],
        "min": date[4],
        "lat": fuji.latitude,
        "lon": fuji.longitude 
    })
    req = request.urlopen(url + param).read()
    res = json.loads(req.decode("utf-8"))
    altitude = float(res["result"]["altitude"]) 
    azimuth = deg2rad(float(res["result"]["azimuth"])) + np.pi
    points = [fuji]
    for i in range(1,limit+1):
        dist = interval * i
        vheight = validHeight(dist, altitude, fuji.height)
        next = fuji.next(azimuth, dist, vheight, name="{}km".format(dist/1000))
        points.append(next)
    return points

def plot():
    for hour in [5,6]:
        for min in [0, 20, 40]:
            date = f"2021/7/10/{hour}/{min}"
            print(date, "...")
            try:
                points = some_points(interval=100, limit=200, date_str=date)
                points = [p.to_location_format() for p in points]
                x = [i*.1 for i in range(len(points))]
                y1 = [p[4] for p in points]
                y2 = [p[5] for p in points]
                plt.figure(figsize=(15,3))
                plt.plot(x,y1)
                plt.plot(x,y2)
                plt.xlim([0,20])
                plt.ylim([0,4000])
                plt.title(date)
                plt.savefig(f"{date.replace('/','_')}.png")
            except FileNotFoundError:
                print("file not found")
                traceback.print_exc()

if __name__ == "__main__":
    spot = find_spot("2021/7/10/6/0", interval=100)
    print(spot)
    spot = find_spot("2021/7/10/6/0", interval=1000)
    print(spot)
    # plot()
    # next_point()
    # sun()


