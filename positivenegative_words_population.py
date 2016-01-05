from nltk.corpus import wordnet
from nltk.stem import PorterStemmer

import os


input_positive_words=[] #Add the list of positive words here

# Eg. ["happy","cheerful","pleased","contended","content","satisfied","radiant","joyous","ecstatic","overenjoyed","gleeful","merry","joyful","delighted","proud","fulfilled","convinced","lucky","fortunate","well","best","better","felicitous","thankful","grateful","great","awesome"]

input_negative_words=[] #Add the list of negative words here

# Eg. ["bad","worst"]

''' Code to populate the input words from a text file - if necessary'''
# sfp=open("input_positive_words.txt","r")
# sfn=open("input_negative_words.txt","r")
# for word in sfp:
# 	input_positive_words.append(word.strip())
# for word in sfn:
# 	input_negative_words.append(word.strip())


# List for target words
all_positive_words=[]
all_negative_words=[]

ps = PorterStemmer()

#To identify synonyms for positive words. Also finds negatives of positive words (antonyms)
for word in input_positive_words:
	for syn in wordnet.synsets(word):
		for l in syn.lemmas():
			w = ps.stem(l.name())
			if w not in all_positive_words:	all_positive_words.append(w)
			if l.antonyms():
				for n in range(len(l.antonyms())):
					w = ps.stem(l.antonyms()[n].name())
					if w not in all_negative_words:	all_negative_words.append(w)


#To identify synonyms for negative words. Also finds negatives of negative words (antonyms)
for word in input_negative_words:
	for syn in wordnet.synsets(word):
		for l in syn.lemmas():
			w = ps.stem(l.name())
			if w not in all_negative_words:	all_negative_words.append(w)
			if l.antonyms():
				for n in range(len(l.antonyms())):
					w = ps.stem(l.antonyms()[n].name())
					if w not in all_positive_words:	all_positive_words.append(w)

# print "Positive List"
# print " ".join(all_positive_words)
# print "Antonyms List:"
# print " ".join(all_negative_words)

try:
	os.remove("all_positive_words.txt")
	os.remove("all_negative_words.txt")
except:
	pass

fp=open("all_positive_words.txt","w")
fn=open("all_negative_words.txt","w")

for word in all_positive_words:
	fp.write(word+"\n")
for word in all_negative_words:
	fn.write(word+"\n")