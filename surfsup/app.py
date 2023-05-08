# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func #func used as a translater to communicate python and sql syntax 

from flask import Flask, jsonify
import datetime as dt
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
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
    """List all api routes"""
    return(
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
       
        f"Returns dates greater than or equal to the start date entered <br>"
        f"/api/v1.0/<start><br>"
       
        f"Returns dates from the start date to the end date entered <br>"
        f"/api/v1.0/<start>/<end><br>"
    )

@app.route("/api/v1.0/<start>")
def temp_start(start):
     session = Session(engine)
     result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
                             func.max(Measurement.tobs)).filter(Measurement.date >= start).\
                             group_by(Measurement.date).all()
     
     session.close()

     tobs_start_list=[]
     for min, avg, max in result:
        tobs_start_dict = {}
        tobs_start_dict["Min"] = min
        tobs_start_dict["Average"] = avg
        tobs_start_dict["Max"] = max
        tobs_start_list.append(tobs_start_dict)


     return jsonify(tobs_start_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
     session =Session(engine)
     result= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
                             func.max(Measurement.tobs)).filter(Measurement.date >= start).\
                                filter(Measurement.date <= end).group_by(Measurement.date).all()
     session.close()
     tobs_start_list=[]
     for min, avg, max in result:
        tobs_start_dict = {}
        tobs_start_dict["Min"] = min
        tobs_start_dict["Average"] = avg
        tobs_start_dict["Max"] = max
        tobs_start_list.append(tobs_start_dict)


     return jsonify(tobs_start_list)

@app.route("/api/v1.0/precipitation")
def precipitation():
    session =Session(engine)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d')
    year_ago = recent_date - dt.timedelta(days=365)
    precip_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).\
        group_by(Measurement.date).order_by(Measurement.date).all()
    session.close()

    precip= []
    for date, prcp in precip_data:
            prcp_dict ={}
            prcp_dict["Date"] = date
            prcp_dict["Percipitation"] =prcp
            precip.append(prcp_dict)
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def station_list():
    session =Session(engine)

    stations = session.query(Station.station, Station.name).all()
    session.close()
    #create a dictionary
    all_stations = []
    for station, name in stations:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        all_stations.append(station_dict)

    # Return the JSON representation of the list
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def active_stat():
     session = Session(engine)

#find most recent date ang find date 1 year before
     recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
     recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d')
     year_ago = recent_date - dt.timedelta(days=365)

#find the most active station
     sel =[Measurement.station, func.count(Measurement.station)]
     stations_active = session.query(*sel).group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
     
#get all the tobs for the mostactive station for the last year   
     results = session.query(Measurement.tobs).\
        filter(Measurement.station == stations_active[0][0]).\
        filter(Measurement.date >= year_ago).all()
     session.close()

     tobs_list =[]
     for date, tobs in results:
          tobs_dict= {}
          tobs_dict["Date"]= date
          tobs_dict["Tobs"]= tobs
          tobs_list.append(tobs_dict)

     return jsonify(tobs_list)


if __name__ == '__main__':
    app.run(debug=True)