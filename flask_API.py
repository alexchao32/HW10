# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 23:06:04 2019

@author: Alex
"""

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
#engine = create_engine("sqlite:///titanic.sqlite")
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
#session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start-date(YYYY-MM-DD)<br/>"
        f"/api/v1.0/start-date(YYYY-MM-DD)/end-date(YYYY-MM-DD)"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of precipitation data (date, precipitation)"""
    # Query all passengers
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    # Create a dictionary from the row data and append to a list
    prcp_data = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)
    
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all station names"""
    # Query all measurements for stations
    session = Session(engine)
    results = session.query(Measurement.station).all()
    #results = session.query(Measurement.station).distinct()

    # Convert list of tuples into normal list
    all_stations = list(set(list(np.ravel(results))))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of last year's temp observations"""
    # Query all measurements for stations
    session = Session(engine)
    
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date
    # last date is 2017-08-23
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    #results = session.query(Measurement.station).all()
    
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > year_ago).all()
    #results = session.query(Measurement.date, Measurement.prcp).all()

    # Create a dictionary from the row data and append to a list
    tobs_data = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)


@app.route("/api/v1.0/<start>")
def temp_start(start):
    """Search starting from the input start date for all temperature observations, only keeping the min, avg and max"""
    
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    
    tobs_data = []
    for min, max, avg in results:
        tobs_dict = {}
        tobs_dict["minimum_temperature"] = min
        tobs_dict["maximum_temperature"] = max
        tobs_dict["average_temperature"] = avg
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    """Search starting from the input start date for all temperature observations, only keeping the min, avg and max"""
    
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    tobs_data = []
    for min, max, avg in results:
        tobs_dict = {}
        tobs_dict["minimum_temperature"] = min
        tobs_dict["maximum_temperature"] = max
        tobs_dict["average_temperature"] = avg
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

if __name__ == '__main__':
    app.run(debug=True)

    