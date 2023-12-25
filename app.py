from flask import Flask
import redis
import json 
import time 
import requests
from flask_cors import CORS
r = redis.Redis(host='host.docker.internal.redis', port=6379, db=0)
app = Flask(__name__)
CORS(app)

DATA_EXPIRY_LENGTH = 3600 # Seconds, equal to one hour (60*60)

@app.route("/")
def hello_world():
    return "Esteem API"

@app.route("/get-snowy-cities")
def get_snowy_cities():
    def update_snowy_cities():
        r.set('last_updated_timestamp',time.time())
        f = open('./cities.json')
        cities = json.load(f)
        data = {}
        print("trying to update cities")
        for city in cities:
            try:
                request = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={city['latitude']}&longitude={city['longitude']}&hourly=temperature_2m,snowfall&temperature_unit=fahrenheit&precipitation_unit=inch")
                request = request.json()
                print(request)
                data[city['city'] + city['state']] = {
                    "city": city["city"],
                    "state":city["state"],
                    "forecast_hours": request["hourly"]["time"],
                    "snowfall_hours":request["hourly"]["snowfall"]
                }
            except Exception as err:
               print(f"Unexpected {err=}, {type(err)=} when trying to update city")
        if len(data.keys()) != 0:
            r.set("cached_snow_forecast",json.dumps(data))
        return data
    last_updated_timestamp = r.get('last_updated_timestamp')
    cached_snow_forecast = r.get("cached_snow_forecast")
    try:
        cached_snow_forecast = json.loads(cached_snow_forecast)
    except:
        update_snowy_cities()
    if last_updated_timestamp is None or cached_snow_forecast is None or time.time()-float(last_updated_timestamp) > DATA_EXPIRY_LENGTH:
        update_snowy_cities()
    else:
        print('using cached weather data')
        return cached_snow_forecast