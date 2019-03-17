# -*- coding: utf-8 -*-
import pytest
from nameLookupDirectory import NameLookupDirectory
from govSocialMediaAnalyzer import GovernmentSocialMediaAnalyzer


class TestClass(object):

    def test_match_name(self):
        lookup = NameLookupDirectory()
        lookup.add_person_to_lookup_directory("A123",("peter", "alfred", "escher"))
        lookup.add_person_to_lookup_directory("A235",("peter", "escher"))
        lookup.add_person_to_lookup_directory("A345",("peter", "john", "goood"))
        assert lookup.match_name(("peter", "alfred"))[0] == "A123"
        assert lookup.match_name(("peter", "john"))[0] == "A345"
        assert lookup.match_name(("peter", "escher"))[0] is None

    def test_govapi(self):
        api_ch = GovernmentSocialMediaAnalyzer("CH")
        gov_df = api_ch.create_govapi_politican_table()
        tw_df = api_ch.create_tw_politican_table(gov_df)
        gov_df.__str__()
