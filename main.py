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
url_re = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def validate_settings(dict):
    errors = {}
    has_users = "users" in dict
    if not has_users:
        errors['users'] = 'This field is missing.'

    has_parenturi = "parenturi" in dict
    if not has_parenturi:
        errors['parenturi'] = 'This field is missing.'

    if has_users and has_parenturi:
        users = dict['users']
        user_id_pattern = re.compile("^[0-9]+(,[0-9]+)*$")
        if not user_id_pattern.match(users.replace(" ", "")):
            errors['users'] = 'This should be a comma seperated list of Twitter user ids.'
        parenturi = dict['parenturi']
        if not url_re.match(parenturi):
            errors['parenturi'] = 'This should be a valid uri, that points to the aggrigation server.'

    return len(errors) > 0, errors

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
        has_error, errors = validate_settings(request.form)
        if has_error:
            current_app.logger.error('error' + str(errors))
            return render_template('settings.html', errors=errors)
        else:
            users = request.form['users']
            parenturi = request.form['parenturi']

            # remove any old config object from the db
            old = Config.query.first()

            if config is not None:
                db_session.delete(old)

            # add the config to the db
            new = Config(users, parenturi)
            db_session.add(new)

            # commit the db changes
            db_session.commit()

            # when a new config is posted
            # kill the old Miner and start up a new one
            mine.reset_miner(users, parenturi, "Twitter miner one.")

            # return OK
            return render_template('settings.html', config=config, success=True)


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