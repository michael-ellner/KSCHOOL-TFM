#MIKE COMMENTS FOR JUAN (DELETE AFTER READ)
#added collection definition which was missing
#changed lang='EN' to lang='en'
#changed hourP
#added default query

def word_count_tweets_mongo(query='Jets', lang='en', word_num=100, scale='linear', hourP=10000000):
    """
    query=tgoogle trend search query, 
    lang= Language of the tweets, 
    word_num=Top count, 
    scale= Scale of the word count (linear, sqrt, log),
    hourP=Number of hours user wants to execute the wordcount
    """
    
    from pymongo import MongoClient
    import re
    from nltk.tokenize import word_tokenize
    import pandas as pd
    from nltk.corpus import stopwords
    from datetime import datetime, timedelta
    import numpy
    english_stops = set(stopwords.words('english'))
    spanish_stops = set(stopwords.words('spanish'))

    #DB connection
    MONGODB_HOST = 'localhost'
    MONGODB_PORT = 27017
    DBS_NAME = 'KSCHOOL_TFM'
    COLLECTION_NAME = 'tweets'

    connection = MongoClient(MONGODB_HOST, MONGODB_PORT) #getting client
    collection = connection[DBS_NAME][COLLECTION_NAME] #getting db    
  
    tweets_text = [tweet['text'] for tweet in collection.find({"tag": query, "lang" : lang, "dateTime": {"$gte" : datetime.utcnow() - timedelta(hours=hourP)}}, projection={'text':True,'_id':False})]
    regex_1 = re.compile(r'[^x\w\w\Z]')
    regex_2 = re.compile(r"[\w]")
    tweetWords_1=word_tokenize(str(tweets_text).strip('[]').encode('utf-8').lower())
    tweetWords_2=filter(lambda i: not regex_1.search(i) and regex_2.search(i), tweetWords_1)
    tweetWords_3= [word for word in tweetWords_2 if word not in query.lower().split(' ') 
                   and word <> 'rt' 
                   and word <> 'https' 
                   and word <>'http'
                   and word <>'u'
                   and word not in english_stops
                   and word not in spanish_stops]
    df=pd.DataFrame(tweetWords_3, columns=['text'])
    dfJ=df.groupby(['text']).size().rename('size').reset_index().sort_values(by='size', ascending=False).head(word_num)
    
    #####
    if scale == "sqrt":
        dfJ['size']=dfJ['size'].apply(numpy.sqrt)
    elif scale=="log":
        dfJ['size']=dfJ['size'].apply(numpy.log)
    else:
        dfJ['size']=dfJ['size']
    
    return  dfJ.to_dict(orient='record ')
