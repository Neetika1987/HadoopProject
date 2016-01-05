#!/usr/bin/env python
#!/usr/bin/python
import sys
import os.path
from hadoop_mongo import BSONReducer
import re
from nltk.corpus import wordnet
from nltk.stem import PorterStemmer

# to extrack link from tweet
def extract_link(text):
	regex = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
	match = re.search(regex, text)
	if match:
		return match.group().encode('utf-8')
	return ''

# function to extract the money from the deal tweet for iphone
def extract_money(tweet, keyword):
	results = re.findall(r'[deals]? \$(\d+) [deals]?', tweet)

	if results:
		match = re.search(r""+keyword+"\s(\w+\s){0,1}", tweet, re.I)
		money = None
		if match:
			money = match.group().strip().encode('utf-8')

		link = extract_link(tweet)

		return [results[0].encode('utf-8'), link, money]

# fetch the products in comparison with iphone
def comparisons(tweet, keyword):
	results = re.findall(r"(\w+\s+\w+\s)vs\s"+keyword+"\s", tweet, re.I)

	if not results:
		results = re.findall(r""+keyword+"\s[\w+\s]+vs\s(\w+\s+\w+\s)", tweet, re.I)
		if results:
			return results[0].strip().encode('utf-8')
	else:
		return results[0].strip().encode('utf-8')

	return "NOTHING"

# function to build positive words hash
def build_positive_hash():
	input_positive_words=["happy","cheerful","pleased","contended","content","satisfied","radiant","joyous","ecstatic","overenjoyed","gleeful","merry","joyful","delighted","proud","fulfilled","convinced","lucky","fortunate","well","best","better","felicitous","thankful","grateful","great","awesome"]

	positive_words = {}
	ps = PorterStemmer()
	for word in input_positive_words:
		for syn in wordnet.synsets(word):
			for l in syn.lemmas():
				word = l.name().strip()
				stemmed = ps.stem(l.name())
				if stemmed not in positive_words:
					positive_words[stemmed] = 1

	return positive_words

# function to build negative words hash
def build_negative_hash():
	input_negative_words = ["bad", "worst", "aweful"]

	negative_words = {}
	ps = PorterStemmer()
	for word in input_negative_words:
		for syn in wordnet.synsets(word):
			for l in syn.lemmas():
				word = l.name().strip()
				stemmed = ps.stem(l.name())
				if stemmed not in negative_words:
					negative_words[stemmed] = 1

	return negative_words

# function to count the number of positive words present  a tweet
def check_for_positive(tweet, positive_words):
	words = tweet.split(' ')
	count = 0
	ps = PorterStemmer()
	for word in words:
		stemmed = ps.stem(word)
		if stemmed in positive_words:
			count += 1

	return count

# function to count the number of negative words present in a tweet
def check_for_negative(tweet, negative_words):
	words = tweet.split(' ')
	count = 0
	ps = PorterStemmer()
	for word in words:
		stemmed = ps.stem(word)
		if stemmed in negative_words:
			count += 1

	return count

def reducer(key, values):

	# fetches the keyword that was specified in search
	productfile = open("productname.txt", "r")
	product_name = str(productfile.read())
	product_name = product_name[:-1]
	productfile.close()

	products = {}
	offers = {}

	generic_positive_words = build_positive_hash()
	generic_negative_words = build_negative_hash()

	filename = product_name+".csv"

	if not os.path.isfile(filename):
		file1 = open(filename, "a")
		file1.write("Country,Good,Bad\n")

	if key == "emotion":
		file1 = open(filename, "a")
		#file1.write("Country,Good,Bad\n")
		countries = {}
		goodcount, badcount = 0, 0
		for v in values:
			values = v['tweet'].split("$$")
			tweet, country = values[0], values[1]
			goodcount = check_for_positive(tweet, generic_positive_words)
			badcount = check_for_negative(tweet, generic_negative_words)
			if country in countries:
				countries[country]['positive'] = countries[country]['positive'] + goodcount

				countries[country]['negative'] = countries[country]['negative'] + badcount
			else:
				countries[country] = {}
				countries[country]['positive'] = goodcount
				countries[country]['negative'] = badcount
		
		for country in countries:
			if (countries[country]['positive'] > 0 and countries[country]['negative'] > 0):
				try:
					value = str(country)+","+str(countries[country]['positive'])+","+str(countries[country]['negative'])+"\n"
					file1.write(value)
				except UnicodeEncodeError:
					continue

		file1.close()
	# logic to handle comparison tweets
	elif key == "comparison":
		file1 = open(filename, "a")
		
		for v in values:
			product = comparisons(v['tweet'], product_name)
			if not product in products:
				products[product] = 1
			else:
				products[product] += 1

		del products["NOTHING"]

		productsstring = ""
		for product in products:
			if products[product] > 1:
				productsstring += product + "~"
				
		productsstring = productsstring[:-1]
		productsstring = productsstring.replace('\n','')

		file1.write("Products,"+productsstring+",##\n")
		
		file1.close()
	# logic to handle deal tweets
	elif key == "deal":
		file1 = open(filename, "a")
		file1.write("Offers,")
		names = {}
		for v in values:
			[name, link, money] = extract_money(v['tweet'], product_name)
			if name and link and money:
				if name not in names:
					names[name] = [name, link, money]
				else:
					alreadypresentmoney = names[name][2]
					if money > alreadypresentmoney:
						names[name] = [name, link, money]

		dealstring = ""
		for name in names:
			[product, link, money] = names[name]
			if product and link and money:
				dealstring += product+"::"+money+"::"+link+"::"
		
		dealstring = dealstring[:-2]
		file1.write(dealstring+"\n")		
		
		file1.close()


	return {'_id': key, 'tweet': "values"}

BSONReducer(reducer)