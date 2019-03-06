from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,func
import datetime as dt
import numpy as np


#Setup Database
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

app = Flask(__name__)


# Convert the query results to a Dictionary using date
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    query_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    data = session.query(func.sum(Measurement.prcp).label('percp'),Measurement.date)\
    .filter(Measurement.date >= query_date)\
    .group_by(Measurement.date)\
    .all()
    print(data)

    response = {}

    for row in data:
        response[row[1]] = row[0]

    return jsonify(response)


# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    q = session.query(
        Station.station,
        Station.name,
        Station.latitude,
        Station.longitude,
        Station.elevation
    ).all()

    output = []

    for station, name, latitude, longitude, elevation in q:
        row = {
            "station": station,
            "name" : name,
            "latitude" : latitude,
            "longitude" : longitude,
            "elevation" : elevation
        }

        output.append(row)
    return jsonify(output)
    
#query for the dates and temperature observations from a year from the last data point.
#Return a JSON list of Temperature Observations (tobs) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    query_date = dt.date(2017, 8,23) - dt.timedelta(days=365)
    q= session.query(Measurement.tobs)\
    .filter(Measurement.date >= query_date)\
    .order_by(Measurement.date.asc())\
    .all()

    all_tobs = list(np.ravel(q))
    
    return jsonify(all_tobs)

#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>")
def range_start(start):
    q = start_query(start).all()
    return jsonify(list(np.ravel(q)))

@app.route("/api/v1.0/<start>/<end>")
def range_start_end(start,end):
    q = start_query(start)\
    .filter(Measurement.date <= end)\
    .all()
    return jsonify(list(np.ravel(q)))

def start_query(start):
    q = session.query(
    func.min(Measurement.tobs),
    func.avg(Measurement.tobs),
    func.max(Measurement.tobs)
    )\
    .filter(Measurement.date >= start)
    return q

if __name__ == "__main__":
    app.run(debug=True)
