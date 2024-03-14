

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

import datetime


# Database Setup
database_path = "sqlite:///001-Resources/hawaii.sqlite"

# Create engine
engine = create_engine(database_path)
Base = automap_base()

Base.prepare(engine, reflect=True)
Base.classes.keys()
inspector = inspect(engine)

print('')
print('********* Measurement Table **********')
columns = inspector.get_columns('measurement')
for i in columns:
    print(i["name"], i["type"])

print('')


print('********* Station Table **********')
columns = inspector.get_columns('station')
for i in columns:
    print(i["name"], i["type"])
print('')


Measurement = Base.classes.measurement
Station =  Base.classes.station


from flask import Flask, jsonify

app = Flask(__name__)



############################################
#### ROUTES
############################################
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        "Welcome to the home page!!!!!</br>"
        + "-----------------------------</br>"
        + "Available Routes</br>"
        + '-----------------------------</br>'
        + '/api/v1.0/precipitation</br>'
        + '/api/v1.0/stations</br>'
        + '/api/v1.0/tobs</br>'
        + '/api/v1.0/start_year-start_month-start_day ' + '---------------@  ' + 'Example: ' + 'http://127.0.0.1:5000//api/v1.0/2017-08-01 </br>'
        + '/api/v1.0/start_year-start_month-start_day/end_year-end_month-end_day' + '---------------@  ' + 'Example: ' + 'http://127.0.0.1:5000//api/v1.0/2017-08-01/2017-08-31'
    )



############################################
#### PRECIPITATION
############################################
@app.route("/api/v1.0/precipitation")
def precipitation():

    print("Server received request for 'Precipitation' page...")
    #return "Welcome to Latyr's 'Precipitation' page!!!!!"
    
    SESSION = Session(engine)

    RESULTS = SESSION.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.desc()).all()
    
    SESSION.close()

    Precipitation_Data = []

    for date, prcp in RESULTS:
        Precipitation_dict = {}
        Precipitation_dict["Date"] = date
        Precipitation_dict["Precipitation"] = prcp
        Precipitation_Data.append(Precipitation_dict)
    return jsonify(Precipitation_Data)



############################################
#### STATION
############################################
@app.route("/api/v1.0/stations")
def station():
    print("Server received request for 'Stations' page...")

    SESSION = Session(engine)

    SELECT = [Station.name]
    INNER_JOIN = [Measurement.station == Station.station]

    RESULTS = SESSION.query(*SELECT).filter(*INNER_JOIN).group_by(*SELECT).order_by(*SELECT).all()
    
    SESSION.close()

    STATION_DATA = []

    for name, in RESULTS:
        STATION_DICT = {}
        STATION_DICT["Station"] = name
        STATION_DATA.append(STATION_DICT)
    return jsonify(STATION_DATA)



############################################
#### TOBS
############################################
@app.route("/api/v1.0/tobs")
def tobs():
    
    print("Server received request for 'Temperatures Observed' page...")

    SESSION = Session(engine)

    ############## MOST ACTIVE STATION - LAST YEAR
    SELECT = [Station.name, func.max(Measurement.tobs)]
    INNER_JOIN = [Measurement.station == Station.station]
    DATE_CONSTRAINT = [Measurement.date > '2016-08-23']
    RESULTS = SESSION.query(*SELECT).filter(*INNER_JOIN).filter(*DATE_CONSTRAINT).all()

    ############## TOBS - LAST YEAR
    #SELECT_2 = [Station.name, Measurement.tobs]
    #RESULTS_2 = SESSION.query(*SELECT_2).filter(*INNER_JOIN).filter(*DATE_CONSTRAINT).all()

    SESSION.close()

    ############## MOST ACTIVE STATION - LAST YEAR
    MAX_STATION_TOBS = []

    for name, tobs, in RESULTS:
        MAX_STATION_DICT = {}
        MAX_STATION_DICT["Station"] = name
        MAX_STATION_DICT["TOBS"]    = tobs     
        MAX_STATION_TOBS.append(MAX_STATION_DICT)
    return jsonify(MAX_STATION_TOBS)

    ############## TOBS - LAST YEAR
    #TOBS_DATA = []

    #for name, tobs, in RESULTS_2:
        #TOBS_DATA_DICT = {}
        #TOBS_DATA_DICT["Station"] = name
        #TOBS_DATA_DICT["TOBS"] = tobs     
        #TOBS_DATA.append(TOBS_DATA_DICT)
    #return jsonify(TOBS_DATA)

    

############################################
#### START
############################################
@app.route("/api/v1.0/<start_year>-<start_month>-<start_day>")
def start(start_year, start_month, start_day):
    print("Server received request for 'Start' page...")

    SESSION = Session(engine)

    SELECT = [
        Station.name,
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs),
    ]
    INNER_JOIN = [Measurement.station == Station.station] 
    YEAR = int(start_year)
    MONTH = int(start_month)
    DAY = int(start_day)
    START_DATE = datetime.date(YEAR, MONTH, DAY)
    DATE_CONSTRAINT = [ Measurement.date >= START_DATE ]
    RESULTS = SESSION.query(*SELECT).\
        filter(*INNER_JOIN).\
            filter(*DATE_CONSTRAINT).\
                group_by(Station.name).\
                    all()

    SESSION.close()


    START_TOBS = []
    print("from: " + str(START_DATE))
    for i in RESULTS:
        START_TOBS_DICT = {}
        START_TOBS_DICT["START ONLY"] = "from: " + str(START_DATE)
        START_TOBS_DICT["NAME"]     = i[0]
        START_TOBS_DICT["MIN TOBS"] = i[1]
        START_TOBS_DICT["AVG TOBS"] = i[2]
        START_TOBS_DICT["MAX TOBS"] = i[3]
        START_TOBS.append(START_TOBS_DICT)
    return jsonify(START_TOBS)



############################################
#### START & END
############################################
@app.route("/api/v1.0/<start_year>-<start_month>-<start_day>/<end_year>-<end_month>-<end_day>")
def startend(start_year, start_month, start_day, end_year, end_month, end_day):
    print("Server received request for 'Start-End' page...")

    SESSION = Session(engine)

    SELECT = [
        Station.name,
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs),
    ]
    
    INNER_JOIN = [Measurement.station == Station.station]
    
    START_YEAR = int(start_year)
    START_MONTH = int(start_month)
    START_DAY = int(start_day)
    START_DATE = datetime.date(START_YEAR, START_MONTH, START_DAY)
    
    END_YEAR = int(end_year)
    END_MONTH = int(end_month)
    END_DAY = int(end_day)    
    END_DATE = datetime.date(END_YEAR, END_MONTH, END_DAY)

    DATE_CONSTRAINT_START = [ Measurement.date >= START_DATE ]
    DATE_CONSTRAINT_END = [ Measurement.date <= END_DATE ]

    RESULTS = SESSION.query(*SELECT).\
        filter(*INNER_JOIN).\
            filter(*DATE_CONSTRAINT_START).\
                filter(*DATE_CONSTRAINT_END).\
                    group_by (Station.name).\
                        all()

    SESSION.close()

    START_END_TOBS = []
    print("from: " + str(START_DATE) + " to: " + str(END_DATE))

    for i in RESULTS:
        START_END_TOBS_DICT = {}
        START_END_TOBS_DICT["START & END"] = "from: " + str(START_DATE) + " to: " + str(END_DATE)
        START_END_TOBS_DICT["NAME"]     = i[0]
        START_END_TOBS_DICT["MIN TOBS"] = i[1]
        START_END_TOBS_DICT["AVG TOBS"] = i[2]
        START_END_TOBS_DICT["MAX TOBS"] = i[3]
        START_END_TOBS.append(START_END_TOBS_DICT)
    return jsonify(START_END_TOBS)


if __name__ == "__main__":
    app.run(debug=True)


