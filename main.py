import re

import flask
from flask import request
from flask import render_template
from flask import current_app

import yaml

import mine

# setup the Flask app
app = flask.Flask(__name__)
app.config['DEBUG'] = True

# load up the settings
settings_file = open('settings.yaml')
settings_dict = yaml.safe_load(settings_file)
settings_file.close()

# start up the miner
users = settings_dict['settings']['users']
parenturi = settings_dict['settings']['parenturi']
name = settings_dict['settings']['name']
mine.reset_miner(users, parenturi, name)

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

    has_name = "name" in dict
    if not has_name:
        errors['name'] = 'This field is missing.'

    has_users = "users" in dict
    if not has_users:
        errors['users'] = 'This field is missing.'

    has_parenturi = "parenturi" in dict
    if not has_parenturi:
        errors['parenturi'] = 'This field is missing.'

    if has_name and has_users and has_parenturi:
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

    if request.method == 'GET':
        # render the form
        return render_template('settings.html', settings=settings_dict['settings'])
    elif request.method == 'POST':
        has_error, errors = validate_settings(request.form)
        if has_error:
            current_app.logger.error('error' + str(errors))
            return render_template('settings.html', errors=errors)
        else:
            users = request.form['users']
            parenturi = request.form['parenturi']
            name = request.form['name']

            # when a new config is posted
            # kill the old Miner and start up a new one
            mine.reset_miner(users, parenturi, name)

            # return OK
            return render_template('settings.html', settings=settings_dict['settings'], success=True)


# start the flask loop
app.run()