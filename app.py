from flask import Flask, jsonify
import pandas as pd
import datetime as dt
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine, inspect, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


app = Flask(__name__)

@app.route("/")
def welcome():
	return (
	    f"Hawaii Weather API!<br/>"
	    f"Available Routes:<br/>"
	    f"/api/v1.0/precipitation<br/>"
	    f"/api/v1.0/stations<br/>"
	    f"/api/v1.0/2015/2018<br/>"
	    f"/api/v1.0/2016<br/>"
	    f"/api/v1.0/tobs<br/>"
	)

@app.route("/api/v1.0/precipitation")
def precipitation():
	# Create our session (link) from Python to the DB
	session = Session(engine)
	date_list = session.query(Measurement.date).all()
	prcp_list = session.query(Measurement.prcp).all()
	session.close()
	prcp_date_dict = {date_list[i][0]: prcp_list[i][0] for i in range(len(date_list))}
	return jsonify(prcp_date_dict)


@app.route("/api/v1.0/stations")
def stations():
	session = Session(engine)
	station_list = session.query(Station.station).all()
	session.close()
	return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
	session = Session(engine)
	station_list = pd.DataFrame(session.query(Measurement.station).all())
	activest_station = station_list.value_counts().keys()[0]
	last_date = session.query(func.max(Measurement.date)).scalar()
	year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days = 365)
	temps = []
	for row in session.query(Measurement.date,Measurement.tobs).all():
	    if row.date >= dt.datetime.strftime(year_ago, '%Y-%m-%d'):
	        temps.append(row.tobs)
	session.close()
	return jsonify(temps)

@app.route("/api/v1.0/<start>", defaults = {'end': None})
@app.route("/api/v1.0/<start>/<end>")
def period(start,end):
	session = Session(engine)
	measurement_df = pd.DataFrame(session.query(Measurement.date,Measurement.tobs).all())
	session.close()
	measurement_df = measurement_df[(measurement_df.date >= start)]
	if end:
		measurement_df = measurement_df[measurement_df.date <= end]
	TAVG = measurement_df['tobs'].mean()
	TMAX = measurement_df['tobs'].max()
	TMIN = measurement_df['tobs'].min()
	return jsonify([TMIN,TAVG,TMAX])


if __name__ == "__main__":
	app.run(debug=True)
