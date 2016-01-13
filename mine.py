from collections import defaultdict
from datetime import datetime
import extract
import json
import thread
import urllib2

import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream


def package_to_json(tweet_id, terms_dict, datetime, mined_at):
    posts = [{
           "terms": terms_dict,
           "url": "http://www.twitter.com/statuses/" + str(tweet_id),
           "datetime": datetime,
           "mined_at": mined_at
    }]
    values = {
       "posts": posts,
       "miner_id": id_of_miner
    }
    data = json.dumps(values)
    return data


def send_to_server(url, data):
    url = url + "/v1/minerpost"
    req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
    try:
        response = urllib2.urlopen(req)
        # print("Response is " + str(response.getcode()))
    except Exception as e:
        print "Exception while sending data to engine."
        print e
        # print traceback.format_exc()


class StdOutListener(StreamListener):

    def on_data(self, data):
        dict = json.loads(data)
        if not "text" in dict:
            print "Text is missing from the tweet body."
            print dict
        else:
            terms_dict = extract.process_status(dict['text'])
            tweet_id = dict['id']
            timestamp_ms = dict['timestamp_ms']
            timestamp = datetime.fromtimestamp(timestamp_ms).strftime('%Y%m%d%H%M')
            now = datetime.now().strftime('%Y%m%d%H%M')  # time.mktime(datetime.now().timetuple())

            # send the tweet to the aggrigator
            url = uriForParent
            data = package_to_json(tweet_id, terms_dict, timestamp, now)
            send_to_server(url, data)
        return True

    def on_error(self, status):
        print "{} http status in response from Twitter.  Recovering ...".format(status)

stream = None

# def start_stream(auth, follow):
#     while True:
#         try:
#             listener = StdOutListener()
#             stream = Stream(auth, listener)
#             stream.filter(follow=follow, async=True)
#             # stream.filter(locations=[-122.75,36.8,-121.75,37.8], async=True) # this is for debug, provides more Test Tweets
#         except:
#             continue

def start_stream(auth, follow):
    listener = StdOutListener()
    stream = Stream(auth, listener)
    stream.filter(follow=follow, async=True)
    # stream.filter(locations=[-122.75,36.8,-121.75,37.8], async=True) # this is for debug, provides more Test Tweets


def download_timelines(auth, follow):
    api = tweepy.API(auth)
    for user_name in follow.split(','):
        user = api.get_user(user_name)
        page_list = []
        for page in tweepy.Cursor(api.user_timeline, user_id=user.id, count=800, include_rts=True).pages(16):
            page_list.append(page)
        for idx, page in enumerate(page_list):
            print "user:{} page:{}/{} statuses:{}".format(user_name, idx, len(page_list), len(page))
            for status in page:
                terms_dict = extract.process_status(status.text)
                created_at = status.created_at.strftime('%Y%m%d%H%M')
                now = datetime.now().strftime('%Y%m%d%H%M')
                json_out = package_to_json(status.id, terms_dict, created_at, now)
                send_to_server(uriForParent, json_out)


def start_mining(miner_id, follow, parenturi, miner_name, consumer_key, consumer_secret, access_token, access_secret):
    global uriForParent
    global nameOfMiner
    global id_of_miner
    id_of_miner = miner_id
    uriForParent = parenturi
    nameOfMiner = miner_name
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    thread.start_new_thread(download_timelines, (auth, follow))
    start_stream(auth, follow)


def stop_mining():
    stream.close()


def reset_miner(miner_id, follow, parenturi, miner_name, consumer_key, consumer_secret, access_token, access_secret):
    if stream != None:
        stop_mining()
    start_mining(miner_id, follow, parenturi, miner_name, consumer_key, consumer_secret, access_token, access_secret)