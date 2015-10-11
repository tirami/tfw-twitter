from collections import defaultdict
import json

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from database import db_session
from model import Tweet

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
            if nouns.count() > 0:
                terms_dict = defaultdict(int)
                for noun in nouns:
                    terms_dict[noun] += 1
                tweet_id = dict['id']
                timestamp_ms = dict['timestamp_ms']

                tweet = Tweet(tweet_id, terms_dict, timestamp_ms)
                db_session.add(tweet)
                db_session.commit()

        return True

    def on_error(self, status):
        print status

stream = None
app = None

def start_mining(follow):
    listener = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    stream = Stream(auth, listener)
    stream.filter(follow=follow, async=True)
    # stream.filter(locations=[-122.75,36.8,-121.75,37.8], async=True)


def stop_mining():
    stream.close()


def reset_miner(follow):
    if stream != None:
        stop_mining()
    start_mining(follow)