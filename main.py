import flask
import flask.ext.sqlalchemy
import flask.ext.restless

from flask_restless_swagger import SwagAPIManager as APIManager

# Create the Flask application and the Flask-SQLAlchemy object.
app = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = flask.ext.sqlalchemy.SQLAlchemy(app)

class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Unicode)

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.Unicode)
    value = db.Column(db.Unicode)

db.create_all()

manager = APIManager(app, flask_sqlalchemy_db=db)

# /api/tweet>
manager.create_api(Tweet, methods=['GET'])
manager.create_api(Setting, methods=['GET', 'POST', 'PUT', 'DELETE'])

# start the flask loop
app.run()