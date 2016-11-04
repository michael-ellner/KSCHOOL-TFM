import json
from flask import Flask
from flask.ext import restful #need to install cors: pip install -U flask-cors #pip install -U flask-restful
from flask import request
from flask.ext.cors import CORS
from word_count import word_count_tweets_mongo
from maptweets import mapbubbles_tweets_mongo
import pickle

app = Flask(__name__)
api = restful.Api(app)
cors = CORS(app, resources={r"/*": {"origins": "*", "allow_headers":["Authorization"]}})


# Load csv with tailored geonames info
geonameid_info_dict = pickle.load(open('../geonames/geonameid_info_dict.p'))
name_geonameidLIST_dict = pickle.load(open('../geonames/name_geonameidLIST_dict.p'))
asciiname_geonameidLIST_dict = pickle.load(open('../geonames/asciiname_geonameidLIST_dict.p'))
altnames_geonameidLIST_dict = pickle.load(open('../geonames/altnames_geonameidLIST_dict.p'))

class orequest(restful.Resource):
    def get(self):
        print request.args
        args = request.args.to_dict()

        if 't' in args.keys(): 
            t = args.pop('t')
        else:
            t='wc'
        print args, t
      
        if t=='map':
            print 'map'
            bubbles, countriesINFO = mapbubbles_tweets_mongo(geonameid_info_dict = geonameid_info_dict, 
                                           name_geonameidLIST_dict = name_geonameidLIST_dict, 
                                           asciiname_geonameidLIST_dict = asciiname_geonameidLIST_dict, 
                                           altnames_geonameidLIST_dict = altnames_geonameidLIST_dict,
                                           **args)
            print 'return map'
            print bubbles
            print 
            print countriesINFO
            return [bubbles, countriesINFO]
        elif t=='wc':
            print 'wc'
            wc =  word_count_tweets_mongo(**args) 
            print 'return wc'
            return wc 
        return None
print 'webserver up and running'
api.add_resource(orequest, '/api/dataframe')
 
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8090,threaded=True)
