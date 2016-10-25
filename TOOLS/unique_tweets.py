#first I delete empty files in bash: find . -size -3 -delete

import os
import json

path0 = '../twitter_google_v6/Data/JSON/'

try:
    os.makedirs(path0 + '/UNIQUE_TWEETS/')
except:
    pass
    
for geo in ['GB','MX','US','ES']:
    path = path0 + geo + '/'

    for starts_with in set(map(lambda x: x.split('_' + geo)[0], os.listdir(path))):
        prefixed = [filename for filename in os.listdir(path) if filename.startswith(starts_with)]
        
        ids_to_keep=[]
        tweets_to_keep=[]
    
        for fname in prefixed:
            tweets = json.load(open(path + fname))
            for tweet in tweets:
                if tweet['id'] not in ids_to_keep:
                    ids_to_keep+=[tweet['id']]
                    tweets_to_keep+=[tweet]
                    
        json.dump(tweets_to_keep,open(path0 + '/UNIQUE_TWEETS/' + starts_with + '_' + geo + '.json', 'w'))
