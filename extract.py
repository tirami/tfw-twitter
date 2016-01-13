from collections import defaultdict
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
import re

tknzr = TweetTokenizer()
stop = stopwords.words('english')


def remove_rt(text):
    return text.replace('RT', '')


def remove_urls(text):
    url_re = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.sub(url_re, '', text, flags=re.MULTILINE)


def remove_non_whitelisted_characters(text):
    regex = re.compile('[^@a-zA-Z\s]')
    return regex.sub('', text)


def process_status(text):
    text = remove_urls(text)
    text = remove_rt(text)
    text = remove_non_whitelisted_characters(text)
    tokens = tknzr.tokenize(text)
    terms = [word for word in tokens if word not in stopwords.words('english')]
    terms_dict = defaultdict(int)
    for noun in terms:
        terms_dict[noun] += 1
    return terms_dict
