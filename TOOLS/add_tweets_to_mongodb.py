from pymongo import MongoClient
from pymongo.helpers import DuplicateKeyError
import os
import re
import json

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'KSCHOOL_TFM'
COLLECTION_NAME = 'tweets'

connection = MongoClient(MONGODB_HOST, MONGODB_PORT) #getting client
collection = connection[DBS_NAME][COLLECTION_NAME] #getting db

path = '../twitter_google_v4/Data/JSON/UNIQUE_TWEETS/'
for fname in os.listdir(path):
    tweets = json.load(open(path+fname)) 
    for tweet in tweets:
        tweet['_id']=tweet['id'] #use unique id of tweet as id for mongodb
        tweet['tags']=re.split('_[A-Z]+.json',fname)[0] #create tags key and include google query
        
        try:
            post_id = collection.insert_one(tweet).inserted_id
        except DuplicateKeyError:
            print 'Dublicate key, id: {}'.format(tweet['_id'])
        except:
            print 'Failed to insert tweet to mongodb, id {}'.format(tweet['_id'])

