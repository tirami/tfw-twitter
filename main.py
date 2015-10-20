import re

import flask
from flask import jsonify
from flask import request
from flask import render_template
from flask import current_app

from database import init_db
from model import Config
from model import Tweet
import mine

import validators

# setup the Flask app
app = flask.Flask(__name__)
app.config['DEBUG'] = True

# setup the database
init_db()
from database import db_session

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

#########
# Util
#########
def has_keys(keys, dict):
    return all (k in keys for k in dict)


def validate_config(dict):
    errors = {}
    if dict == None:
        errors['main'] = 'Body not present.  Content-Type might be wrong.'
    if len(dict) <= 0 or not has_keys(['users'], dict):
        errors['main'] = 'JSON body does not have the correct keys.'
    users = dict['users']
    pattern = re.compile("^[0-9]+(,[0-9]+)*$")
    if not pattern.match(users.replace(" ", "")):
        errors['users'] = 'users argument is wrong format.'
    parenturi = dict['parenturi']
    if not validators.url(parenturi):
        errors['parenturi'] = 'parenturi is not a valid url.'
    return len(errors) <= 0, errors

#########
# Routes
#########
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    # get the settings
    config = Config.query.first()

    if request.method == 'GET':
        # render the form
        return render_template('settings.html', config=config)
    elif request.method == 'POST':
        has_error, errors = validate_config(request.form)
        if has_error:
            current_app.logger.error('error' + errors)
            return render_template('settings.html', errors)
        else:
            if config is not None:
                db_session.delete(old)

            # add the config to the db
            new = Config(users)
            db_session.add(new)

            # commit the db changes
            db_session.commit()

            # when a new config is posted
            # kill the old Miner and start up a new one
            mine.reset_miner(users)

            # return OK
            return 'New configuration saved.', 200


@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        # filter out anything that is posted that is not an integer
        json = request.get_json()
        if json == None:
            return 'JSON body not present.  Content-Type must be set to application/json.'
        if len(json) <= 0 or not has_keys(['users'], json):
            return 'JSON body does not have the correct keys.', 400
        users = json['users']
        pattern = re.compile("^[0-9]+(,[0-9]+)*$")
        if not pattern.match(users.replace(" ", "")):
            return 'JSON body is wrong format.', 400

        # remove any old config object from the db
        old = Config.query.first()
        if old is not None:
            db_session.delete(old)

        # add the config to the db
        new = Config(users)
        db_session.add(new)

        # commit the db changes
        db_session.commit()

        # when a new config is posted
        # kill the old Miner and start up a new one
        mine.reset_miner(users)

        # return OK
        return 'New configuration saved.', 200


    elif request.method == 'GET':
        # retrive the current configuration and return it
        c = Config.query.first()
        if c == None:
            c = { 'users' : '' }
        return jsonify(users=c.users)


@app.route('/posts', methods=['GET'])
def posts():
    if request.method == 'GET':
        timestamp = 0
        ts_arg = request.args.get('timestamp')
        if ts_arg != None:
            pattern = re.compile("[0-9]+")
            if pattern.match(ts_arg):
                timestamp = int(ts_arg)
            else:
                return 'timestamp query parameter is malformed.', 400
        tweets = Tweet.query.filter(Tweet.timestamp_ms >= timestamp).all()
        return jsonify(posts=[i.serialize() for i in tweets])

# start the flask loop
app.run()