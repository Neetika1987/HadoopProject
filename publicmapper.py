#!/usr/bin/env python
import sys
import re
from hadoop_mongo import BSONMapper

# classify a tweet as deal tweet
def matchmoney(tweet):
	results = re.search(r'[deals]? \$(\d+) [deals]?', tweet)

	if results:
		return 1
	else:
		return 0

# classify a tweet as Product Comparison
def has_comparison(tweet):
	results = re.search(r'\svs\s', tweet)
	if results:
		return 1
	else:
		return 0

def mapper(documents):
	for doc in documents:
		tweet = doc['text']
		if doc['place']:
			country = doc['place']['country_code']
			yield {'_id': "emotion", 'tweet': tweet + "$$" + country}
		elif matchmoney(tweet):
			yield {'_id': "deal", 'tweet': tweet}
		elif has_comparison(tweet):
			yield {'_id': "comparison", 'tweet': tweet}

BSONMapper(mapper)
print >> sys.stderr, "Done Mapping."
