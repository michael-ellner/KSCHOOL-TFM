import re
import tweepy
import os
import time
import json
from pytrends.request import TrendReq
import sys
from pymongo import MongoClient
from pymongo.helpers import DuplicateKeyError
import datetime
from time import gmtime, strftime


def tweet_created_at_to_datetime(create_at):
    dt = create_at.split()
    year = int(dt[5])
    month = {'Jan':1, 'Feb':2, 'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}[dt[1]]
    day = int(dt[2])
    hms=dt[3].split(':')
    hour = int(hms[0])
    minute = int(hms[1])
    second = int(hms[2])
    return datetime.datetime(**{'year':year, 'month':month,'day':day,'hour':hour,'minute':minute,'second':second})

def get_formated_localtime():
    return strftime("%a %b %d %H:%M:%S +0000 %Y", gmtime())


def get_hot_trends(hottrends_payload, pytrend, geo, collection):
    XRF = pytrend.hottrendsdetail(hottrends_payload) #extract top trends from XML rss feed 
    qs = re.findall('<title>(.*)</title>', XRF)[1:]   #discard frist term: top trends

    hottrends = {'qs': qs, 'dateTime'.decode():datetime.datetime.utcnow(), 'formated_time' : get_formated_localtime(), 'geo' : geo }
    try:
        post_id = collection.insert_one(hottrends).inserted_id
    except DuplicateKeyError:
        print 'Dublicate key, id'
    except:
        print 'Failed to insert hottrend'


    return qs

def get_google_hist(trend_payload, pytrend):
    trend = pytrend.trend(trend_payload)
    search_7d = pytrend.trend(trend_payload)
    localtime = get_formated_localtime()
    fname = trend_payload['q'] + '_' + trend_payload['geo'] + '_' + localtime + '.json'
    json.dump(search_7d, open(fname ,'w'))

def main(argv):        


    def get_twitter_data(apisearch_dict, geo, max_tweets, api,collection):
        path = 'Data/JSON/' + geo + '/'
        if not os.path.exists(path):
            os.makedirs(path)
    
        localtime = get_formated_localtime()
        searched_tweets = [status for status in tweepy.Cursor(api.search, **apisearch_dict).items(max_tweets)]
    
        json_str = map(lambda x: x._json, searched_tweets)
        fname = apisearch_dict['q'] + '_' + geo + '_' + localtime + '.json'
        json.dump(json_str, open(path + fname, 'w'))

        #add tweets to database
        for tweet in json_str:
            tweet['dateTime'.decode()]=datetime.datetime.strptime(tweet[u'created_at'],"%a %b %d %H:%M:%S +0000 %Y")
            tweet['_id'.decode()]=tweet['id'] #use unique id of tweet as id for mongodb
            tweet['tag'.decode()]=apisearch_dict['q']
            try:
                post_id = collection.insert_one(tweet).inserted_id
            except DuplicateKeyError:
                print 'Dublicate key, id: {}'.format(tweet['_id'])
            except:
                print 'Failed to insert tweet to mongodb, id {}'.format(tweet['_id'])




        return len(searched_tweets)

    
    #google auth
    google_username = ##############################
    google_password = ##############################
    pytrend = TrendReq(google_username, google_password, custom_useragent='My Pytrends Script')
    #twitter auth
    consumer_key=##############################
    consumer_secret=##############################
    access_token=##############################
    access_token_secret=##############################



    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    
    geos = ['ES','US','MX','GB']
    codes = ['p26','p1','p21','p9']
    coordinates = [ [40,-4,150], [39.828175,-98.5795,1400], [23,-102,900], [54,-4,250] ]
    new_tweets = 900
    refresh_tweets = 90
    twitter_sleep_secs = 15.1*60

    MONGODB_HOST = 'localhost'
    MONGODB_PORT = 27017
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT) #getting client

    DBS_NAME = 'KSCHOOL_TFM'

    COLLECTION_NAME = 'tweets'
    collection_tweets = connection[DBS_NAME][COLLECTION_NAME] #getting db
    COLLECTION_NAME = 'google_hottrends'
    collection_google_hottrends = connection[DBS_NAME][COLLECTION_NAME] #getting db


    tweets_counter = 0
    while True:
        for geo, code, coordinate in zip(geos, codes, coordinates):
            #get 20 trends of country
            attempts = 0
            while attempts < 10:
                try:
                    print( 'get_hot_trends', geo, get_formated_localtime() )
                    qs = get_hot_trends( hottrends_payload={'pn' : code}, pytrend=pytrend, geo=geo, collection=collection_google_hottrends)
                    break
                except:
                    print( 'failed get_hot_trends', attempts, get_formated_localtime() )
                    time.sleep(20)
                    attempts += 1
            
            for q  in qs:
                #get google search history
                #attempts = 0
                #while attempts < 10:
                #    try:
                #        print( 'get_google_hist', geo, q, get_formated_localtime() )
                #        get_google_hist( trend_payload={'q': q, 'geo':geo, 'date': 'today 7-d'}, pytrend=pytrend )
                #        break
                #    except:
                #        print( 'failed get_hot_trends', attempts, get_formated_localtime() )
                #        time.sleep(20)
                #        attempts+=1

                #get twitter data of geo
                ##get last id of latest tweet in database


                for lang in ['es','en']:

                    max_tweets = new_tweets
                    since_id = 0
                    last_tweet = collection_tweets.find_one({'tag' : q, 'lang':lang}, projection = {'_id': True, 'created_at':True}, sort=[('_id' ,-1)] )
                    if last_tweet:
                        since_id = int(last_tweet['_id'])
                        if (datetime.datetime.utcnow() - tweet_created_at_to_datetime(last_tweet['created_at'])).days < 1: 
                            max_tweets = refresh_tweets
    
                    attempts = 0
                    while attempts < 10:
                        try:
                            #if max_tweets > 1800 - tweets_counter:
                            #    print "sleep for twitter" 
                            #    time.sleep(twitter_sleep_secs)
                            #    tweets_counter = 0

                            print( "get_twitter_data", lang, geo, q, since_id, max_tweets, get_formated_localtime() )
                            n = get_twitter_data( apisearch_dict = {'q' : q, 'result_type' : 'mixed', 'since_id': since_id, 'lang':lang}, 
                                                  geo = geo, max_tweets = max_tweets, api = api, collection = collection_tweets)
                            tweets_counter += n
                            print( "tweets_counter",n, tweets_counter)
                            break
                        except:
                            print( "failed get_twitter_data, will sleep, redindex database, and reset tweets_counter", attempts, get_formated_localtime() )
                            t1 = time.time()
                            collection_tweets.reindex()
                            dt = time.time() - t1
                            print("took {} minutes to redindex database".format(dt/60.))
                            time.sleep(twitter_sleep_secs - dt)
                            tweets_counter = 0
                            attempts+=1



if __name__ == "__main__":
    main(sys.argv)
