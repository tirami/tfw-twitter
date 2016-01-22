from mining.forms import TextField, URLField
import mining.views as views
from miner import TwitterMiner

form_fields = {
    'name': TextField('name', 'Name', 'Name of the miner.'),
    'parent_uri': URLField('parent_uri', 'Engine URL', 'Url of the engine.'),
    'users': TextField('users', 'Accounts to Mine', 'Comma separated list of Twitter user names.'),
    'access_secret': TextField('access_secret', 'Access Secret', 'Access Secret for Twitter API.'),
    'access_token': TextField('access_token', 'Access Token', 'Access Token for Twitter API.'),
    'consumer_key': TextField('consumer_key', 'Consumer Key', 'Consumer Key for Twitter API.'),
    'consumer_secret': TextField('consumer_secret', 'Consumer Secret', 'Consumer Secret for Twitter API.')
}


def run():
    # configure the service
    views.miner_cls = TwitterMiner
    views.form_fields = form_fields
    views.app.run()


if __name__ == "__main__":
    run()

