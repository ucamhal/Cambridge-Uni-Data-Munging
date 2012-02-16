from collections import defaultdict
from math import log, e
from operator import add

class NaiveBayesClassifier(object):
    def __init__(self):
        self.entries = defaultdict(lambda: 0)
        self.words = defaultdict(lambda: defaultdict(lambda: 1))
    
    def train(self, words, tag):
        self.entries[tag] += 1
        for word in words:
            self.words[tag][word] += 1
    
    def _log_score(self, tag, words):
        return reduce(add, (log(self.words[tag][w]) for w in words), 0)
    
    def classify(self, words):
        (score, tag) = max(((log(count) + self._log_score(tag, words), tag)
                            for (tag, count) in self.entries.items()))
        return (tag, e ** score)