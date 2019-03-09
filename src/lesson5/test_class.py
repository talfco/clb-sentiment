# -*- coding: utf-8 -*-
import pytest
from namematching import sort_words,normalize_unicode_to_ascii,double_metaphone,double_metaphone_compare, Threshold

class TestClass(object):

    def test_normalize_unicode_to_ascii(self):
        data = u'Marta Flückiger-Bäni'
        norm = normalize_unicode_to_ascii(data)
        assert norm == "marta fluckiger bani"
        data = u'Marta  -  Flückiger-Bäni'
        norm = normalize_unicode_to_ascii(data)
        assert norm == "marta fluckiger bani"
        assert sort_words(norm) == "bani fluckiger marta"

    def test_double_metaphone(self):
        tp1 = double_metaphone(u'LilianeMauryPasquier')
        tp2 = double_metaphone(u'liliane Maury Pasquier')
        assert True == double_metaphone_compare(tp1,tp2,Threshold.STRONG)
        tp1 = double_metaphone(u'L. Maury Pasquier')
        tp2 = double_metaphone(u'liliane Maury Pasquier')
        assert False == double_metaphone_compare(tp1,tp2,Threshold.STRONG)
        tp1 = double_metaphone(u'Marta Flückiger-Bäni')
        tp2 = double_metaphone(u'Marta Fluckiger-Bani')
        assert True == double_metaphone_compare(tp1,tp2,Threshold.STRONG)
        tp1 = double_metaphone(u'Marta Flückiger-Bäni')
        tp2 = double_metaphone(u'Marta Flükger-Bäni')
        assert True == double_metaphone_compare(tp1,tp2,Threshold.NORMAL)
