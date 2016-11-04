from flask import Flask, render_template
from flask.ext.pymongo import PyMongo
from bson.json_util import dumps
from datetime import datetime, timedelta

app=Flask(__name__)

app.config['MONGO_DBNAME']='KSCHOOL_TFM'
app.config['MONGO_URI']='mongodb://localhost:27017/KSCHOOL_TFM'
mongo=PyMongo(app)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def trends_default(path):
    #List of counrties with google trends
    geo_hottrends=country_list()
    # Country of trends
    country_of_trends=country_map("US")
    #List of trends google trends
    trends, trend_date, trend_date_url=google_trends(country="US",dayP=0)
    return render_template("index.html", 
        geo_hottrends=geo_hottrends, 
        country_of_trends=country_of_trends, 
        trends=trends,
        trend_date=trend_date,
        trend_date_url=trend_date_url,
        tweet_id='451399393850052610')

@app.route("/map")
def map_location():
    return render_template("map.html")

@app.route("/query")
def barchart_time():
    date_count=[{'count': 1, 'date': '24-10-2016-12'},{'count': 1, 'date': '24-10-2016-13'},{'count': 5, 'date': '24-10-2016-18'},{'count': 13, 'date': '23-10-2016-23'},{'count': 2, 'date': '24-10-2016-11'}].dumps
    return render_template("barchart_time.html",
        date_count=date_count)

@app.route("/wc_cloud")
def wc_cloud():
    return render_template("wc_cloud.html")

@app.route("/<country>/<dayP>")
def trends(country,dayP):
	#List of counrties with google trends
    geo_hottrends=country_list()
    # Country of trends
    country_of_trends=country_map(country)
    #List of trends google trends
    trends, trend_date, trend_date_url=google_trends(country=country,dayP=dayP)
    return render_template("index.html", 
        geo_hottrends=geo_hottrends, 
        country_of_trends=country_of_trends, 
        trends=trends,
        trend_date=trend_date,
        trend_date_url=trend_date_url,
        country=country,
        dayP=dayP,
        tweet_id='451399393850052610')

def google_trends(country="US", dayP=0, dt=None):
    google_hottrends=mongo.db.google_hottrends
    if not dt:
        dt=google_hottrends.find_one({"geo": country}, sort=[("dateTime",-1)])['dateTime']- timedelta(days=int(dayP))
    hottrends = [query['qs'] for query in google_hottrends.find({"geo": country, "dateTime": {"$gte" : datetime(dt.year,dt.month,dt.day), "$lte" : datetime(dt.year,dt.month,dt.day)+timedelta(days=1)}}, projection={'qs':True,'_id':False})] 
    l=[]
    for ht in hottrends:
        l+=ht
    return set(l), str(dt.strftime("%B"))+' '+str(dt.day)+', '+str(dt.year), str(dt.year)+'-'+str(dt.month)+'-'+str(dt.day) 

def country_map(country):
        if country=='ES':
            return 'ES', 'Spain'
        elif country=='GB':
            return 'GB', 'Great Britain'
        elif country=='MX':
            return 'MX', 'Mexico'
        elif country=='US':
            return 'US', 'United States'

def country_list():
    google_hottrends=mongo.db.google_hottrends
    return map(country_map, set([query['geo'] for query in google_hottrends.find(projection={'geo':True,'_id':False})]))



if __name__== '__main__':
    app.run(port=4000 ,debug=True)