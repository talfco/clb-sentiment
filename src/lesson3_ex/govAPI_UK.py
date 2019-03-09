from govAPI import GovAPI
import requests


class GovAPI_UK(GovAPI):

    def __init__(self, cfg):
        self.__cfg = cfg

    def _get_active(self,dict):
        return True

    def _get_id(self,dict):
        link = dict.get('_about')
        return link[33:]

    def _get_last_name(self,dict):
        if  dict.get('familyName') == None:
            return None
        return dict.get('familyName').get("_value")

    def _get_first_name(self,dict):
        if  dict.get('givenName') == None:
            return None
        return dict.get('givenName').get("_value")

    def _get_party(self,dict):
        if  dict.get('party') == None:
            return None
        return dict.get('party').get("_value")

    def _get_gender(self,dict):
        if  dict.get('gender') == None:
            return None
        return dict.get('gender').get("_value")

    def load_government_members(self):
        page_number=0
        url = self.__cfg['govAPIUrl']
        politician_res = self.__cfg['govAPICouncillorsRes']
        par = self.__cfg['govAPIParams']
        result_number = 0
        while True:
            par[0]['_page'] = str(page_number)
            headers = requests.utils.default_headers()
            headers.update({ 'User-Agent': 'Mozilla/5.0'})
            politicians = requests.get(url+politician_res, params=par[0], headers=headers).json()
            total_results = politicians.get('result').get('totalResults')
            items = politicians['result']['items']
            for politician in items:
                self._add_person_record(politician)
            result_number += 500
            if result_number > total_results:
                break
            else:
                page_number += 1
        return self._members
