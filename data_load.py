import sys
import jsonpickle
import os
import json
import tweepy
from pymongo import MongoClient

# API KEY for the Twitter
API_KEY = "CoBPMQYNM0qm9RcmHsUy1x58R"
API_SECRET = "w3S6VNovIXgemSn9YvhGOHTJseuFnduxvTZd7iO3GQVMNUuTOT"

auth = tweepy.AppAuthHandler(API_KEY, API_SECRET)
 
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

if (not api):
    print ("Can't Authenticate")
    sys.exit(-1)

# storing the search query in the variable searchQuery
searchQuery = str(sys.argv[1])

# maximum number of tweets
maxTweets = 10000

# number of tweets to be fetched per API call
tweetsPerQry = 100

# latest id of the tweet
sinceId = 0

# max id of the tweet
max_id = -1L

# variable to store the tweet count
tweetCount = 0

# A hash to store the twitter ids
ids = {}

# Setting up MongoDB
client = MongoClient("0.0.0.0")
# selects the default database 'test'
db = client.test
# selects the collection 'product'

collection = db.product

while tweetCount < maxTweets:
    try:
        if (max_id <= 0):
            if (not sinceId):
                new_tweets = api.search(q=searchQuery, count=tweetsPerQry, lang="en")
            else:
                new_tweets = api.search(q=searchQuery, count=tweetsPerQry, since_id=sinceId, lang="en")
        else:
            if (not sinceId):
                new_tweets = api.search(q=searchQuery, count=tweetsPerQry, max_id=str(max_id - 1), lang="en")
            else:
                new_tweets = api.search(q=searchQuery, count=tweetsPerQry, max_id=str(max_id - 1), since_id=sinceId, lang="en")

        if not new_tweets:
            print("No more tweets found")
            break

        for tweet in new_tweets:
            json_str = json.dumps(tweet._json)
            stuff = json.loads(json_str)
            if not stuff['id'] in ids:
                result = collection.insert_one(stuff)
                print result.inserted_id
                ids[stuff['id']] = 1
        tweetCount += len(new_tweets)
        max_id = new_tweets[-1].id
    except tweepy.TweepError as e:
        print("Error : " + str(e))
        break