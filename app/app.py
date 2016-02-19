from mining.forms import TextField, URLField, IntegerField
import mining.views as views
from miner import TwitterMiner

form_fields = {
    'name': TextField('name', 'Name', 'Name of the miner.'),
    'parent_uri': URLField('parent_uri', 'Engine URL', 'Url of the engine.'),
    'users': TextField('users', 'Accounts to Mine', 'Comma separated list of Twitter user names.'),
    'batch_size': IntegerField('batch_size', 'Batch Size', 'Tweets per post to server.'),
    'queue_time': IntegerField('queue_time', 'Queue Time', 'Number of seconds to wait before sending any queued Tweets to the server regardless of time.'),
    'access_secret': TextField('access_secret', 'Access Secret', 'Access Secret for Twitter API.'),
    'access_token': TextField('access_token', 'Access Token', 'Access Token for Twitter API.'),
    'consumer_key': TextField('consumer_key', 'Consumer Key', 'Consumer Key for Twitter API.'),
    'consumer_secret': TextField('consumer_secret', 'Consumer Secret', 'Consumer Secret for Twitter API.')
}


def run():
    # configure the service
    views.miner_cls = TwitterMiner
    views.form_fields = form_fields
    # views.app.run(host='0.0.0.0')
    views.app.run()


if __name__ == "__main__":
    run()

