from sqlalchemy import Column, Integer, Unicode
from database import Base

import json

#########
# Models
#########
class Config(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True)
    users = Column(Unicode)
    parenturi = Column(Unicode)

    def __init__(self, users):
        self.users = users

    def __repr__(self):
        return '<Config id:%d, users:%s, parenturi:%s>' % (self.id, self.users, self.parenturi)


class Tweet(Base):
    __tablename__ = 'tweet'
    id = Column(Integer, primary_key=True)
    tweet_id = Column(Integer)
    terms = Column(Unicode)
    timestamp_ms = Column(Integer)

    def __init__(self, tweet_id, terms_dict, timestamp_ms):
        self.tweet_id = tweet_id
        self.terms = json.dumps(terms_dict)
        self.timestamp_ms = timestamp_ms

    def __repr__(self):
        return '<Tweet id:%d, terms:%s, ts:%s>' % (self.id, self.terms, self.timestamp_ms)

    def serialize(self):
        return {
           'tweet_id' : self.tweet_id,
           'terms': self.terms,
           'timestamp_ms' : self.timestamp_ms
        }