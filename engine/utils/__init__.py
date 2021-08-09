import numpy as np

def deg2rad(deg: float) -> float:
    return np.pi * deg / 180

def rad2deg(rad: float) -> float:
    return rad * 180 / np.pi


R = 63781370  # earth radius <meter>
AngularDiameter = deg2rad(0.53)


from .exceptions import *
from .point import *
from .compass import *
from .date2spot import *
from .spot2date import *

if __name__ == "__main__":
    import datetime as dt
    fuji = Point( 35.362797, 138.730878, elevation=3776, name="Mt.Fuji")
    date = dt.datetime(2021, 3, 23, 12, 0)
    sun_direction(fuji, date)