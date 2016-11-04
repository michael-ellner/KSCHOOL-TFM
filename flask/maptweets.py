def mapbubbles_tweets_mongo(query='Jets', hourP=1000000, geonameid_info_dict=None,
                                                         name_geonameidLIST_dict=None,
                                                         asciiname_geonameidLIST_dict=None,
                                                         altnames_geonameidLIST_dict=None):                                           

    import pickle
    import unicodedata
    from datetime import datetime, timedelta
    from pymongo import MongoClient
    import pandas as pd
    #DB connection
    MONGODB_HOST = 'localhost'
    MONGODB_PORT = 27017
    DBS_NAME = 'KSCHOOL_TFM'
    COLLECTION_NAME = 'tweets'
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT) #getting client
    collection = connection[DBS_NAME][COLLECTION_NAME] #getting db  
    
    # Load csv with tailored geonames info
    geonameid_info_dict = pickle.load(open('../geonames/geonameid_info_dict.p'))
    name_geonameidLIST_dict = pickle.load(open('../geonames/name_geonameidLIST_dict.p'))
    asciiname_geonameidLIST_dict = pickle.load(open('../geonames/asciiname_geonameidLIST_dict.p'))
    altnames_geonameidLIST_dict = pickle.load(open('../geonames/altnames_geonameidLIST_dict.p'))
    
    
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
    
    
    
    #How do I know if geoid corresponds to county? feature code == PCLI
    #map(lambda x: geonameid_info_dict[x]['name'], filter(lambda x: geonameid_info_dict[x]['feature code']=='PCLI', geonameid_info_dict.keys()))
    
    
    #DATAMAPS works with ISO3 and geonames database with ISO. Thus I'll load csv that has both infos and create a transformation dictionary
    fields = ['ISO', 'ISO3', 'ISO-Numeric', 'fips', 'Country', 'Capital', 'Area(in sq km)', 'Population', 'Continent', 'tld', 'CurrencyCode', 'CurrencyName', 'Phone', 'Postal Code Format', 'Postal Code Regex', 'Languages', 'geonameid', 'neighbours', 'EquivalentFipsCode']
    df = pd.read_csv("../geonames/countryInfo.txt",sep='\t',names=fields,comment='#')
    df = df[['ISO','ISO3']]
    df = df.dropna()
    df = df.set_index(df['ISO'].values)
    df = df['ISO3']
    ISO_to_ISO3 =df.to_dict()
    
    
    
    def datamap_bubbles_countriesINFO(tweet, exclude_countries=True):
        bubbles = dict()
        countriesINFO = dict()
    
        for tweet in tweets:
            location = tweet['user']['location']
            info, geoid = geotag_location(location)
            if info:
                try:
                    ISO3 = ISO_to_ISO3[info['country code']]
                except:
                    ISO3 = None
                    
                if ISO3:
                    if ISO3 in countriesINFO:
                        countriesINFO[ISO3]['tweetIDs'] += [tweet['id_str']]
                    else:
                        countriesINFO[ISO3] = {'tweetIDs': [tweet['id_str']],'name':info['country code'] }
    
                if exclude_countries and info['feature code']!='PCLI': #do not include countries in bubbles (if exclude countries)
                
                    if geoid in bubbles:
                        bubbles[geoid]['radius'] += 1
                        bubbles[geoid]['radius'] = max(bubbles[geoid]['radius'], 10)
                        bubbles[geoid]['tweetIDs'] += [tweet['id_str']]
                    else:
                        bubbles[geoid] = {'fillKey':tweet['lang'] , 'tweetIDs': [tweet['id_str']],  'latitude': info['latitude'], 'longitude': info['longitude'],'radius': 1, 'name':info['name']}
        return bubbles.values(), countriesINFO
    
    #def datamap_color(locations):
        
        
    #return query, datetime.utcnow() - timedelta(hours=hourP)
    print("start map query")
    tweets = [tweet for tweet in collection.find({"tag": query,
                                                      "dateTime": {"$gte" : datetime.utcnow() - timedelta(hours=hourP)}},
                                                     projection={'user.location':True, 'lang':True, 'id_str':True}).limit(100)]
    
    print("finished map query")
    
    bubbles, countriesINFO = datamap_bubbles_countriesINFO([tweet for tweet in tweets])
    for bubble in bubbles:
        bubble['n_tweets'] = len(bubble['tweetIDs'])
    
    for ISO3 in countriesINFO.keys():
        countriesINFO[ISO3]['n_tweets'] = len(countriesINFO[ISO3]['tweetIDs'])
    
        
    return bubbles, countriesINFO
