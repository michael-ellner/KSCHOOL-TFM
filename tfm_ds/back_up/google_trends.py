from flask import Flask
from flask.ext.pymongo import PyMongo
from bson.json_util import dumps

app= Flask(__name__)

app.config['MONGO_DBNAME']='KSCHOOL_TFM'
app.config['MONGO_URI']='mongodb://localhost:27017/KSCHOOL_TFM'

mongo=PyMongo(app)

@app.route('/trends/<country>', methods=['GET'])
def google_hottrends(country="US"):
    google_hottrends=mongo.db.google_hottrends
    hottrends = [query['qs'] for query in google_hottrends.find({"geo": country}, projection={'qs':True,'_id':False})] 

    l=[]
    for ht in hottrends:
    	l+=ht
    return dumps(list(set(l)))

if __name__== '__main__':
    app.run(port=4000 ,debug=True)