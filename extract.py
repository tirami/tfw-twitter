from collections import defaultdict
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
import re
import string

tknzr = TweetTokenizer()
stop = stopwords.words('english')


def remove_hash_tags(text):
    return text.replace('#', '')


def remove_rt(text):
    return text.replace('RT', '')


def remove_punctuation(text):
    exclude = set(string.punctuation)
    s = ''.join(ch for ch in text if ch not in exclude)
    return s


def remove_urls(text):
    url_re = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.sub(url_re, '', text, flags=re.MULTILINE)


def process_status(text):
    text = remove_hash_tags(text)
    text = remove_urls(text)
    text = remove_rt(text)
    text = remove_punctuation(text)
    tokens = tknzr.tokenize(text)
    print tokens
    terms = [word for word in tokens if word not in stopwords.words('english')]
    terms_dict = defaultdict(int)
    for noun in terms:
        terms_dict[noun] += 1
    return terms_dict
