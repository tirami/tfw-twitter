from collections import defaultdict
import json
import urllib2

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

consumer_key = 'A8BdqFZb6pX6nzdC55b7xJbaJ'
consumer_secret = 'fyRbYzEDlfP6lLilmN6Sl5laaTW0NWRdKevWnI1dGwvCbbJBIL'
access_token = '36620718-PAlXuTv5nVo1mRyPf7CqHzCgtMT84pkFksdososs0'
access_secret = 'oY6CJphyCXsfQnj1h680ovhdPFoSWK9msAp34IHU4sRNx'

tknzr = TweetTokenizer()
stop = stopwords.words('english')

class StdOutListener(StreamListener):

    def on_data(self, data):
        dict = json.loads(data)
        if not "text" in dict:
            print dict
        else:
            tokens = tknzr.tokenize(dict['text'])
            tagged = nltk.pos_tag(tokens)
            nouns = [word for (word, type) in tagged if type == 'NN'] # can be a noun or a hashtag
            if len(nouns) > 0:
                terms_dict = defaultdict(int)
                for noun in nouns:
                    terms_dict[noun] += 1
                tweet_id = dict['id']
                timestamp_ms = dict['timestamp_ms']

                # send the tweet to the aggrigator
                url = uriForParent
                values = {
                       "post": {
                           "terms": terms_dict,
                           "url": "http://www.twitter.com/statuses/" + str(tweet_id),
                           "datetime": timestamp_ms,
                           "mined_at": timestamp_ms
                       },
                   "miner_id": nameOfMiner
                }
                data = json.dumps(values)
                req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
                try:
                    response = urllib2.urlopen(req)
                    print response.read()
                except:
                    print "Error with aggrigation server."
            else:
                print "No nouns."
        return True

    def on_error(self, status):
        print status

stream = None

def start_mining(follow, parenturi, miner_name):
    global uriForParent
    global nameOfMiner

    uriForParent = parenturi
    nameOfMiner = miner_name

    listener = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    stream = Stream(auth, listener)
    stream.filter(follow=follow, async=True)
    # stream.filter(locations=[-122.75,36.8,-121.75,37.8], async=True) # this is for debug, provides more Test Tweets


def stop_mining():
    stream.close()


def reset_miner(follow, parenturi, miner_name):
    if stream != None:
        stop_mining()
    start_mining(follow, parenturi, miner_name)