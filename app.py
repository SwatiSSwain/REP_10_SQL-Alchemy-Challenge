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
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
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
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/><br/>"
        f"Return a dictionary of all dates and precipitation  for the previous year<br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"Return a JSON list of stations from the dataset<br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"Return a JSON list of temperature observations (TOBS) for the previous year<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"Type in a start date in YYYY-MM-DD (%Y-%m-%d) format to get the min, max and avg temperature for all dates greater than and equal to the start date.<br/>"
        f"/api/v1.0/&ltstart&gt</br><br/>"
        f"Type in a start and end date in YYYY-MM-DD (%Y-%m-%d) format to get the min, max and avg temperature for all dates for dates between the start and end date inclusive.<br/>"
        f"/api/v1.0/&ltstart&gt/&ltend&gt"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Return a dictionary of all dates and precipitation values"""

    #Calculate max date in Measurement
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    #Convert tuple to string
    max_date=''.join(max_date)

    #Convert max_date String to Date datatype
    convert_max_date=dt.datetime.strptime(max_date, "%Y-%m-%d")

    #Calculate the date 1 year ago from max_date
    year_ago = dt.date(convert_max_date.year, convert_max_date.month ,convert_max_date.day) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores.
    
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()

    session.close()

    # Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict.update({date:prcp})
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset"""

    # Return a JSON list of stations from the dataset.
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of temperature observations (TOBS) for the previous year"""

    #Calculate max date in Measurement
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    #Convert tuple to string
    max_date=''.join(max_date)
    
    #Convert max_date String to Date datatype
    convert_max_date=dt.datetime.strptime(max_date, "%Y-%m-%d")

    #Calculate the date 1 year ago from max_date
    year_ago = dt.date(convert_max_date.year, convert_max_date.month ,convert_max_date.day) - dt.timedelta(days=365)
     
    #Find most active station for last year
    active_station = session.query(Measurement.station).\
                    filter(Measurement.date >= year_ago).\
                    group_by(Measurement.station).\
                    order_by(func.count(Measurement.tobs).desc()).first()

    active_station=''.join(active_station)

    # Query the temperature observations of the most active station for the last year of data.
    results = session.query(Measurement.tobs).\
                            filter(Measurement.station == active_station).\
                            filter(Measurement.date >= year_ago).\
                            order_by(Measurement.date).all()

    session.close()

    # Convert list of tuples into normal list
    # Return a JSON list of temperature observations (TOBS) for the previous year.

    active_station_tobs = list(np.ravel(results))

    return jsonify(active_station_tobs)

@app.route("/api/v1.0/<start>")
def start_date_range(start):

    """When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date."""

    session = Session(engine)

    # When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
    results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
                            filter(Measurement.date >= start).all()
    
    session.close()

    # Convert list of tuples into normal list
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date.

    start_output = list(np.ravel(results))


    return jsonify(start_output)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):

    """ When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive."""

    session = Session(engine)

    # When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
    results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
                            filter(Measurement.date >= start).\
                            filter(Measurement.date <= end).all()


    session.close()

    # Convert list of tuples into normal list
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.

    start_end_output = list(np.ravel(results))
    
    return jsonify(start_end_output)


if __name__ == '__main__':
    app.run(debug=True)
