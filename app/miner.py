from datetime import datetime
import json
from threading import Event, Thread
import urllib2

import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import mining.extract as extract


class TweetListener(StreamListener):
    def __init__(self, miner_id, parent_uri):
        super(TweetListener, self).__init__()
        self.miner_id = miner_id
        self.parent_uri = parent_uri

    def on_data(self, data):
        status = json.loads(data)
        if "text" not in status:
            print "Text is missing from the tweet body."
            print status
        else:
            # process the tweet
            terms_dict = extract.process_status(status['text'])
            created_at = datetime.strptime(status['created_at'], '%a %b %d %H:%M:%S +0000 %Y').strftime('%Y%m%d%H%M')
            now = datetime.now().strftime('%Y%m%d%H%M')

            # send the tweet to the aggrigator
            url = self.parent_uri
            data = TwitterMiner.package_to_json(self.miner_id, status['id'], terms_dict, created_at, now)
            TwitterMiner.send_to_parent(url, data)
        return True

    def on_error(self, status_code):
        if status_code == 420:
            print "Streaming API rate limit exceeded.  Disconnecting."
        else:
            print "{} http status in response from Twitter.  Recovering ...".format(status_code)


def call_repeatedly(interval, func, *args):
    stopped = Event()

    def loop():
        while not stopped.wait(interval):  # the first call is in `interval` secs
            func(*args)
    Thread(target=loop).start()
    return stopped.set


class TwitterMiner(Thread):
    def __init__(self, category):
        super(TwitterMiner, self).__init__()
        self.category = category
        self.stream = None
        self.is_downloading = False
        self.current_queue = []
        self.stop_timed_queue_flush = None

    def run(self):
        auth = OAuthHandler(self.category.consumer_key,
                            self.category.consumer_secret)
        auth.set_access_token(self.category.access_token,
                              self.category.access_secret)
        api = tweepy.API(auth)
        self.stop_timed_queue_flush = call_repeatedly(60, self.flush_queue)
        self.subscribe_to_tweet_stream(auth, api)
        self.download_timelines(api)

    def stop(self):
        self.log("Stopping miner.")
        self.is_downloading = False
        self.stream.disconnect()
        self.stop_timed_queue_flush()

    def download_timelines(self, api):
        self.is_downloading = True
        for user_name in self.category.users.split(','):
            self.log("Downloading timeline for {}".format(user_name))
            user = api.get_user(user_name)
            page_list = []
            for page in tweepy.Cursor(api.user_timeline, user_id=user.id, count=800, include_rts=True).pages(16):
                page_list.append(page)
            for idx, page in enumerate(page_list):
                self.log("user:{} page:{}/{} statuses:{}".format(user_name, idx, len(page_list), len(page)))
                for status in page:
                    terms_dict = extract.process_status(status.text)
                    created_at = status.created_at.strftime('%Y%m%d%H%M')
                    now = datetime.now().strftime('%Y%m%d%H%M')
                    self.queue_for_sending(status.id, terms_dict, created_at, now)
                    if not self.is_downloading:
                        return  # stop downloading

    def subscribe_to_tweet_stream(self, auth, api):
        user_ids = self.resolve_user_ids(api, self.category.users)
        self.log("Subscribing to twitter streams for {}".format(self.category.users))
        listener = TweetListener(self.category.id, self.category.parent_uri)
        self.stream = Stream(auth, listener)
        user_ids_str = [str(user_id) for user_id in user_ids]
        self.stream.filter(follow=user_ids_str, async=True)

    def log(self, text):
        print "Miner:{} - {}".format(self.category.id, text)

    def queue_for_sending(self, tweet_id, terms_dict, now, mined_at):
        post = TwitterMiner.dict_of_post(tweet_id, terms_dict, now, mined_at)
        self.current_queue.append(post)
        queue_size = len(self.current_queue)
        if queue_size >= self.category.batch_size:
            self.flush_queue()

    def flush_queue(self):
        self.log("Sending Tweets to Server.  Batch size {}".format(len(self.current_queue)))
        json_body = TwitterMiner.package_batch_to_json(self.category.id, self.current_queue)
        TwitterMiner.send_to_parent(self.category.parent_uri, json_body)
        self.current_queue = []


    @staticmethod
    def dict_of_post(post_id, terms_dict, datetime, mined_at):
        post = {
           "terms": terms_dict,
           "url": "http://www.twitter.com/statuses/" + str(post_id),
           "datetime": datetime,
           "mined_at": mined_at
        }
        return post

    @staticmethod
    def resolve_user_ids(api, users):
        user_ids = []
        username_list = users.split(',')
        for username in username_list:
            username = username.strip()
            user = api.get_user(username)
            user_ids.append(user.id)
        return user_ids

    @staticmethod
    def send_to_parent(url, data):
        url += "/v1/minerpost"
        req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
        try:
            urllib2.urlopen(req)
        except Exception as e:
            print "Exception while sending data to engine at the uri: {}".format(url)
            print e

    @staticmethod
    def package_batch_to_json(id_of_miner, posts):
        values = {
           "posts": posts,
           "miner_id": id_of_miner
        }
        data = json.dumps(values)
        return data
