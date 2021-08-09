import numpy as np
from typing import List, Optional, Dict, Tuple, Generator
import datetime as dt

from . import R, AngularDiameter, deg2rad, rad2deg
from .point import Point, validElevation
from .compass import astro_rise_set, astro_direction


def daterange( start: dt.date,
               end: dt.date,
               ) -> Generator[dt.date, None, None]:
    days = int((end - start).days)
    for day in range(days):
        yield start + dt.timedelta(day)

def search_dt( root_point: Point,
               spot: Point,
               year: int,
               ) -> List[str,]:
    valt, vazm = _valid_altitude_azimuth( root_point, spot )
    print(valt, vazm)
    alt_tolerance = AngularDiameter * 0.25
    start = dt.date(year, 7, 1)
    end   = dt.date(year, 7,31)
    dates_viewable = []
    for date in daterange(start, end):
        date_str = f"{year}/{date.month}/{date.day}"
        time_str = _ViewableTime( date_str, spot, valt, vazm, alt_tolerance)
        if time_str is not None:
            dates_viewable.append( f"{date_str}/{time_str}" )
    return dates_viewable

def _ViewableTime( date: dt.date,
                   spot: Point,
                   altitude: float,  #[0, pi/2]
                   azimuth: float,   #[0, 2pi]
                   alt_tolerance: float,  #[0, pi/2]
                   ) -> Optional[str]:
    
    #return (altitude, time_str) at best azimuth
    def _binary_search( left: int,
                        right: int,
                        ) -> Tuple[float, str]:
        mid = (left + right) // 2
        hour, min = mid//60, mid%60
        result = astro_direction( "SUN", spot, f"{date}/{hour}/{min}" )
        print("{:.1f}/{:.1f}".format(float(result["azimuth"]), azimuth), end=" | ")
        if left == mid:
            return (float(result["altitude"]), f"{hour}/{min}") 
        if azimuth < float(result["azimuth"]):
            return _binary_search(left, mid)
        return _binary_search(mid, right)

    rise, set = astro_rise_set( "SUN", spot, date )
    rise = rise.hour*60 + rise.minute 
    set = set.hour*60 + set.minute 

    best_alt, best_time = _binary_search(rise, set)
    print("{}: {:.1f}/{:.1f} ({}/{})".format(
        best_time, best_alt, altitude,
        np.abs(altitude - best_alt), alt_tolerance
    ))
    if np.abs(altitude - best_alt) < alt_tolerance:
        return best_time
    return None


def _distant_angle( B: Point, C: Point, format="rad" ) -> float:
    assert format in ["rad", "deg"]
    b = deg2rad( 90 - B.latitude )
    c = deg2rad( 90 - C.latitude )
    alpha = deg2rad( C.longitude - B.longitude )
    a = np.arccos( np.cos(b) * np.cos(c) \
                 + np.sin(b) * np.sin(c) * np.cos(alpha) )
    beta = np.arcsin( np.sin(b) * np.sin(alpha) / np.sin(a) )
    if C.latitude - B.latitude < 0:
        beta = np.pi - beta
    print("{} | alpha={}, a={}, beta={}".format(C.name, rad2deg(alpha), rad2deg(a), rad2deg(beta)))
    if format == "deg":
        a = rad2deg(a)
        b = rad2deg(b)
    return a, beta

def _valid_altitude_azimuth( root_point: Point,
                             spot: Point,
                             ) -> Tuple[float, float]:
    theta, beta = _distant_angle( root_point, spot )
    H0 = R + root_point.elevation
    H1 = R + spot.elevation
    altitude = np.arctan2( H0 - H1*np.cos(theta), H1*np.sin(theta) )
    azimuth = beta
    return rad2deg(altitude), rad2deg(azimuth)

def pointRange( p1: Point,
                p2: Point,
                num: int=100,
                ) -> Generator[Tuple[float, Point], None, None]:
    theta, beta = _distant_angle( p1, p2 )
    delta = theta / (num - 1)
    azimuth = rad2deg(beta)
    for i in range(num):
        a = delta * i
        dist = R * a
        point = p1.next( azimuth, dist, valid_elevation=None, name="{:.1f}km".format(dist/1000))
        yield dist, point

def plot2d( root_point: Point,
            spot: Point,
            ) -> None:
    import matplotlib.pyplot as plt

    X, Y = [], []
    points = [p for (_,p) in pointRange(root_point, spot, 11)] + [spot]
    for point in points:
        X.append(point.longitude)
        Y.append(point.latitude)
    plt.figure(figsize=(6,6))
    plt.plot(X, Y, marker="o", markersize=15, linewidth=1)
    plt.plot([X[0],X[-1]], [Y[0],Y[-1]], marker="o", markersize=15, linewidth=1)
    plt.savefig("{}-{}.png".format(root_point.name, spot.name))

def simulation( root_point: Point,
                spot: Point,
                ) -> None:
    import matplotlib.pyplot as plt

    altitude, azimuth = _valid_altitude_azimuth(root_point, spot)
    X, Y1, Y2 = [], [], []
    for dist, point in pointRange(root_point, spot):
        velev = validElevation(dist, altitude, root_point)
        X.append(dist)
        Y1.append(point.elevation)
        Y2.append(velev)

    plt.figure(figsize=(15,3))
    plt.plot(X,Y1)
    plt.plot(X,Y2)
    # plt.xlim([0,20])
    plt.ylim([0,4000])
    # plt.title(date)
    plt.savefig("{}-{}.png".format(root_point.name, spot.name))



if __name__ == "__main__":
    fuji = Point( 35.362797, 138.730878, elevation=3776, name="Mt_Fuji")
    ymnk = Point( 35.421686, 138.883249, elevation= 985, name="Lake_Yamanaka")
    akis = Point( 35.461181, 138.157325, elevation=3120, name="Mt_Akaishi")
    ihai = Point( 35.223744, 138.810040, elevation=1459, name="Mt_Ihai")
    anmo = Point( 35.279727, 138.630842, elevation= 491, name="Mt_Anmo")
    for spot in [ymnk, akis, ihai, anmo]:
        simulation( fuji, spot )
    # dts = search_dt(fuji, ymnk, 2021)
    # print(dts)