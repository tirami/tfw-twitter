import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer

import json

consumer_key = 'A8BdqFZb6pX6nzdC55b7xJbaJ'
consumer_secret = 'fyRbYzEDlfP6lLilmN6Sl5laaTW0NWRdKevWnI1dGwvCbbJBIL'
access_token = '36620718-PAlXuTv5nVo1mRyPf7CqHzCgtMT84pkFksdososs0'
access_secret = 'oY6CJphyCXsfQnj1h680ovhdPFoSWK9msAp34IHU4sRNx'

tknzr = TweetTokenizer()
stop = stopwords.words('english')

#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):

    def on_data(self, data):
        dict = json.loads(data)
        if not "text" in dict:
            print dict
        else:
            tokens = tknzr.tokenize(dict['text'])
            # words = [w for w in tokens if w not in stop]
            tagged = nltk.pos_tag(tokens)
            nouns = [word for (word, type) in tagged if type == 'NN'] # can be a noun or a hashtag
            print nouns
        return True

    def on_error(self, status):
        print status


if __name__ == '__main__':

    listener = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    stream = Stream(auth, listener)

    stream.filter(locations=[-122.75,36.8,-121.75,37.8])