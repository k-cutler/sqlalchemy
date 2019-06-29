import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import simplejson

import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/Hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return(
        f"Welcome to the Climate App!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precip():
#   query date and precipitation
    results = session.query(Measurement.date, Measurement.prcp).all()
    
    # Create a dictionary from the row data and append to a list of
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["precipiation"] = prcp
        all_prcp.append(prcp_dict)
    
    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)
    
@app.route("/api/v1.0/tobs")
def tobs():
    # what's the latest date?
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latest_date_1 = str(np.ravel(latest_date))

    latest_date_formatted = dt.datetime.strptime(latest_date_1,"['%Y-%m-%d']")

    prior_year = latest_date_formatted - dt.timedelta(days=366)

    # query for date and tobs
    sel = [Measurement.date, Measurement.tobs]
    results = session.query(*sel).filter(Measurement.date >= prior_year)

    # create dictionary of tobs for last year
    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)
    
@app.route("/api/v1.0/<start>")
def start(start):
    # define start (see documentation: https://stackoverflow.com/questions/31669864/date-in-flask-url)
    start = dt.datetime.strptime(start, "%Y-%m-%d").date()

    # query for min, max, avg tobs
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).all()
    results = list(np.ravel(results))

    start_only = []
    start_only_dict = {}
    start_only_dict["min"] = results[0]
    start_only_dict["avg"] = results[1]
    start_only_dict["max"] = results[2]
    start_only.append(start_only_dict)

    return jsonify(start_only)
    
@app.route("/api/v1.0/<start>/<end>")
def end(start,end):
    # define start, end (see documentation: https://stackoverflow.com/questions/31669864/date-in-flask-url)
    start = dt.datetime.strptime(start, "%Y-%m-%d").date()
    end = dt.datetime.strptime(end, "%Y-%m-%d").date()

    # query for min, max, avg tobs
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    results = list(np.ravel(results))

    start_end = []
    start_end_dict = {}
    start_end_dict["min"] = results[0]
    start_end_dict["avg"] = results[1]
    start_end_dict["max"] = results[2]
    start_end.append(start_end_dict)

    return jsonify(start_end)
    
if __name__ == "__main__":
    app.run(debug=True)
