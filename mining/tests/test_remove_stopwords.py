import unittest

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer

tknzr = TweetTokenizer()
stop = stopwords.words('english')
tags_to_remove = ['PRP', 'PRP$', 'RP', 'TO', 'IN']


def remove_stopwords(tagged):
    terms = [word for (word, tag) in tagged if word.lower() not in stop and tag not in tags_to_remove]
    return terms


class MyTest(unittest.TestCase):
    def test(self):
        stops_sentence = u'i me my myself we our ours ourselves you your yours yourself yourselves he him his himself she her hers herself it its itself they them their theirs themselves what which who whom this that these those am is are was were be been being have has had having do does did doing a an the and but if or because as until while of at by for with about against between into through during before after above below to from up down in out on off over under again further then once here there when where why how all any both each few more most other some such no nor not only own same so than too very s t can will just don should now'
        tokens = tknzr.tokenize(stops_sentence)
        tagged = nltk.pos_tag(tokens)
        removed = remove_stopwords(tagged)
        self.assertEqual(len(removed), 0)