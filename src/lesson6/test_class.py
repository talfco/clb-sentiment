# -*- coding: utf-8 -*-
import pytest
from namematching import generateNamePermutationList

class TestClass(object):

    def test_normalize_unicode_to_ascii(self):
        lookup_table = {}
        generateNamePermutationList(lookup_table,"123",["peter", "alfred", "escher"])
