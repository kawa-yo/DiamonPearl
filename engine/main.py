import flask
from flask import Flask, render_template, abort
import pandas as pd
import traceback
from utils import Point, find_all_spots, pointRange
import time
import datetime as dt

DEBUG = True

app = Flask(__name__)
landmarks = [
    ["Mt. Fuji", 35.362797, 138.730878, 3776, 300],
]
# df = pd.read_csv("resource/data.csv")

@app.route("/")
def home():
    return render_template("home.html", title="dp_home", landmarks=landmarks)

@app.route("/from_date", methods=["POST"])
def search_spots_from_date():
    try:
        if flask.request.method == 'POST':
            _idx = int(flask.request.form.get("landmark"))
            selected = landmarks[_idx]
            root_point = Point(selected[1], selected[2], elevation=selected[3], diameter=selected[4], name=selected[0])
            date = map( int, flask.request.form.get("date").split("-") )
            date = dt.date( *date )
            _start_time = time.time()
            # ymnk = Point( 35.421686, 138.883249, elevation=985, name="Lake_Yamanaka")
            # ihai = Point( 35.223744, 138.810040, elevation=1459, name="Mt_Ihai")
            # akis = Point( 35.461181, 138.157325, elevation=3120, name="Mt_Akaishi")
            # _spots = [p for (d,p) in pointRange(root_point, ihai, 11)] + [ihai]
            _spots = find_all_spots( root_point, date, min_interval=5 )
            print("elapsed: {:.1f}s".format(time.time() - _start_time))
            locations = [s.to_location_format() for s in _spots]
            return render_template( "mappage.html",
                                    title="map page",
                                    locations=locations,
                                    DEBUG=DEBUG,
                                    )
        else:
            return abort(400)
    except Exception as e:
        traceback.print_exc()
        return str(e)


if __name__ == "__main__":
    app.run(debug=True)
