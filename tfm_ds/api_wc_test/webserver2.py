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
        return word_count_tweets_mongo(**request.args.to_dict()) 

            
api.add_resource(orequest, '/api/dataframe')
 
if __name__ == '__main__':
    app.run(port=4000,threaded=True)