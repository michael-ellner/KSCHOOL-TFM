import json
from flask import Flask
from flask.ext import restful #need to install cors: pip install -U flask-cors #pip install -U flask-restful
from flask import request
from flask.ext.cors import CORS
from word_count import word_count_tweets_mongo

app = Flask(__name__)
api = restful.Api(app)
cors = CORS(app, resources={r"/*": {"origins": "*", "allow_headers":["Authorization"]}})


class orequest(restful.Resource):
    def get(self):
        print request.args
        return word_count_tweets_mongo(**request.args.to_dict()) 

            
api.add_resource(orequest, '/api/dataframe')
 
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8090,threaded=True)
