# udadisi-twitter
The Twitter miner part of Udadisi project.  The miner is configured with a set of Twitter user ids and then subscribes to their streams.  When a Tweet is recorded, it processes using some simple NLP to extract the interesting words and saves the processed Tweet into a database.  The Tweets can then be retrieved in bulk by the Udadisi Aggrigator.

## Installation
The miner is build using Python 2.7 and the [Flask framework](http://flask.pocoo.org/) and a bunch of other libraries.  Assuming you have an up-to-date Python 2.7 environment, the simplest way to install all the dependencies is to use pip and the requirements file that's in the repository.  The command is:

`pip install -r requirements.txt`

Currently the miner uses sqlite but it will soon be moved to Postgres so that will be a requirement.  Once that's done, just run the main file:

`python main.py`

## Usage
I've included a Swagger YAML file that should explain how the api is used but there are only 2 endpoints

`/config` and `/posts`