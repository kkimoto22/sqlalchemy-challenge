import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Last Year's Temperatures for Most Active Station: /api/v1.0/tobs<br/>"
        f"From Start Date on: /api/v1.0/start<br/>"
        f"From Start Date to End Date: /api/v1.0/start_end<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    query_dates = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= query_dates).order_by(Measurement.date).all()
    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    all_precip = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        all_precip.append(prcp_dict)
    # Return the JSON representation of your dictionary.
    return jsonify(all_precip)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_list = session.query(Station.name).all()
    session.close()

    # Return a JSON list of stations from the dataset
    st = [result[0] for result in station_list]
    return jsonify(st)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Query the dates and temperature observations of the most active station for the last year of data.
    query_dates = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    most_active_station_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281', Measurement.date >= query_dates).\
        order_by((Measurement.date).desc()).all()
    session.close()

    # Return a JSON list of temperature observations (TOBS) for the previous year.
    tob = []
    for date, tobs in most_active_station_data:
        tob_dict = {}
        tob_dict["Date"] = date
        tob_dict["Observed Temp"] = tobs
        tob.append(tob_dict)
    
    return jsonify(tob)

@app.route("/api/v1.0/<start>")
def starter(start):
    session = Session(engine)
    # Return a JSON list of the minimum temperature, the average temperature, and 
    # the max temperature for a given start period
    starts = dt.datetime.strptime(start, "yyyy-mm-dd")
    start_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= starts).all()
    start1=list(np.ravel(start_results))
    session.close()
    return jsonify(start1)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start="yyyy-mm-dd", end="yyyy-mm-dd"):
    session=Session(engine)
    start_end_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start)&(Measurement.date <= end).all()
    session.close()

    # return JSON list
    min = [result[0] for result in start_end_results]
    avg = [result[1] for result in start_end_results]
    max = [result[2] for result in start_end_results]
    return jsonify(min, avg, max)


if __name__ == '__main__':
    app.run(debug=True)