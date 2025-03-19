import re
import csv
import nltk
import yaml
from nltk.corpus import wordnet

class word_syn_replacer(object):
    def __init__(self, word_map):
        self.word_map = word_map

    def replace(self, word):
        return self.word_map.get(word, word)

class CSVword_syn_replacer(word_syn_replacer):
    def __init__(self, fname):
        word_map = {}
        with open(fname, 'r') as file:
            for line in csv.reader(file):
                word, syn = line
                word_map[word] = syn
        super(CSVword_syn_replacer, self).__init__(word_map)

class YAMLword_syn_replacer(word_syn_replacer):
    def __init__(self, fname):
        with open(fname, 'r') as file:
            word_map = yaml.safe_load(file)  
        super(YAMLword_syn_replacer, self).__init__(word_map)
