# -*- coding: utf-8 -*-
# https://gist.github.com/j4mie/557354
# https://github.com/rliebz/whoswho
import re
import unicodedata
import itertools
from metaphone import doublemetaphone
from enum import Enum


class Threshold(Enum):
    WEAK = 0
    NORMAL = 1
    STRONG = 2


""" Normalise (normalize) unicode data in Python to remove umlauts, accents etc. """
def normalize_unicode_to_ascii(data):

    normal = unicodedata.normalize('NFKD', data).encode('ASCII', 'ignore')
    val = normal.decode("utf-8")
    val = val.lower()
    # remove special characters
    val = re.sub('[^A-Za-z0-9 ]+', ' ', val)
    # remove multiple spaces
    val = re.sub(' +', ' ', val)
    return val


def sort_words(words):
    words = words.split(" ")
    words.sort()
    newSentence = " ".join(words)
    return newSentence


def double_metaphone(value):
    return doublemetaphone(value)


#(Primary Key = Primary Key) = Strongest Match
#(Secondary Key = Primary Key) = Normal Match
#(Primary Key = Secondary Key) = Normal Match
#(Alternate Key = Alternate Key) = Minimal Match
def double_metaphone_compare(tuple1,tuple2,threshold):
    if threshold == Threshold.WEAK:
        if tuple1[1] == tuple2[1]:
            return True
    elif threshold == Threshold.NORMAL:
        if tuple1[0] == tuple2[1] or tuple1[1] == tuple2[0]:
            return True
    else:
        if tuple1[0] == tuple2[0]:
            return True
    return False


def generateNamePermutationList(lookup_table, index, name_list):
    perms = []
    perms.extend(itertools.permutations(name_list))
    i = len(name_list)-1
    while i > 0:
        perms.extend(itertools.permutations(name_list,i))
        i -=1

    print("Permutations: "+str(len(perms)))
    print(perms.__str__())
    dict1 = {}
    dict2 = {}
    for entry in perms:
        str1 = ''.join(entry)
        key1 = double_metaphone(str1)[0]
        key2 = double_metaphone(str1)[1]
        dict1[key1] = "12ABC"
        if key2 != '':
            dict2[key2] = "12ABC"


    print(dict1.__str__())
    print(dict2.__str__())
    return perms