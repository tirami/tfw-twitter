import flask
from flask import request
from database import init_db
from model import Config
from database import db_session

from flask import jsonify
import re

import mine

# Create the Flask application and the Flask-SQLAlchemy object.
app = flask.Flask(__name__)
app.config['DEBUG'] = True

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


#########
# Routes
#########
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
        return jsonify(users=c.users)


# start the flask loop
app.run()