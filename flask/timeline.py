def tweets_timeline(query='Jets', hourP=10000):

    from pymongo import MongoClient
    from datetime import datetime, timedelta
    
    MONGODB_HOST = 'localhost'
    MONGODB_PORT = 27017
    DBS_NAME = 'KSCHOOL_TFM'
    COLLECTION_NAME = 'tweets'
    
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT) #getting client
    collection = connection[DBS_NAME][COLLECTION_NAME] #getting db.tweets
    
    print 'tweets_timeline'    
    pipeline_2=[{"$match" : {"dateTime" : {"$gte": datetime.utcnow() - timedelta(hourP) }, "tag": query}},
        {"$group" : {"_id" : {"year" : {"$year": "$dateTime"}, 
                              "month" : {"$month": "$dateTime"}, 
                              "day" : {"$dayOfMonth": "$dateTime"},
                              "hour": {"$hour": "$dateTime"}
                             }, 
                     "count":{"$sum":1}}},
              {"$sort" : {"date" : 1 }}, 
              {"$limit": 100}]
    
    
    
    u=[doc for doc in collection.aggregate(pipeline_2)]
    dts = map(lambda x: x['_id'], u)
    cs = map(lambda x: x['count'], u)
    
    
    
    f = []
    for dt, c in zip(dts,cs):
        l=map(lambda x: str(x), [dt['year'], dt['month'],dt['day'],dt['hour']])
        f+=[{'date' : "-".join(l), 'value':c}]
    return f

