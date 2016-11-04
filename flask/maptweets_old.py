def mapbubbles_tweets_mongo(query='Jets', hourP=1000000, geonameid_info_dict=None,
                                                         name_geonameidLIST_dict=None,
                                                         asciiname_geonameidLIST_dict=None,
                                                         altnames_geonameidLIST_dict=None):                                           
    import pickle
    import unicodedata
    from datetime import datetime, timedelta
    from pymongo import MongoClient
    #DB connection
    MONGODB_HOST = 'localhost'
    MONGODB_PORT = 27017
    DBS_NAME = 'KSCHOOL_TFM'
    COLLECTION_NAME = 'tweets'
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT) #getting client
    collection = connection[DBS_NAME][COLLECTION_NAME] #getting db  
    
    # Load csv with tailored geonames info
    if geonameid_info_dict is None: geonameid_info_dict = pickle.load(open('../geonames/geonameid_info_dict.p'))
    if name_geonameidLIST_dict is None:  name_geonameidLIST_dict = pickle.load(open('../geonames/name_geonameidLIST_dict.p'))
    if asciiname_geonameidLIST_dict is None: asciiname_geonameidLIST_dict = pickle.load(open('../geonames/asciiname_geonameidLIST_dict.p'))
    if altnames_geonameidLIST_dict is None: altnames_geonameidLIST_dict = pickle.load(open('../geonames/altnames_geonameidLIST_dict.p'))

    def geotag_location(location):
        location = location.lower()
        ll=[ location.strip().split(',')[0],
             location.strip().split(' ')[0],
             location.strip().split(' ')[-1],        
             location.strip().split(',')[-1],      
             location.strip().split('/')[0],     
             location.strip().split('/')[-1],        
             location.strip().split('.')[0],        
             location.strip().split('.')[-1],        
             location.strip().split('-')[0],        
             location.strip().split('-')[-1] ]        
        geoids = None
        for l in ll: 
            if l in name_geonameidLIST_dict:
                geoids = name_geonameidLIST_dict[l]
                break
            if l in altnames_geonameidLIST_dict: 
                geoids = altnames_geonameidLIST_dict[l]
                break
            if unicodedata.normalize('NFD', unicode(l)).encode('ASCII', 'ignore') in asciiname_geonameidLIST_dict: 
                geoids = asciiname_geonameidLIST_dict[unicodedata.normalize('NFD', unicode(l)).encode('ASCII', 'ignore')]
                break
        if geoids is None: return None, None
        
        # use geoid from largest population
        geoid = geoids[max(enumerate(map(lambda geoid: geonameid_info_dict[geoid]['population'], geoids)), key=lambda x: x[1])[0]]
    
        info = geonameid_info_dict [ geoid ]
        return info, geoid
    
    def datamap_bubbles(locations):
        bubbles = dict()
        for location in locations:
            info, geoid = geotag_location(location)
            if info:
                if geoid in bubbles:
                    bubbles[geoid]['radius'] += 1
                    bubbles[geoid]['radius'] = max(bubbles[geoid]['radius'], 10)
                else:
                    bubbles[geoid] = {'latitude': info['latitude'], 'longitude': info['longitude'],'radius': 1, 'name':info['name']}
        return bubbles.values()
    
    #return query, datetime.utcnow() - timedelta(hours=hourP)
    print("start map query")
    tweets = [tweet for tweet in collection.find({"tag": query, 
                                                      "dateTime": {"$gte" : datetime.utcnow() - timedelta(hours=hourP)}}, 
                                                     projection={'user.location':True, 'lang':True}).limit(100)]
    print("finished map query")
    return datamap_bubbles([tweet['user']['location'] for tweet in tweets])



