from govAPI import GovAPI
import requests


class GovAPI_CH(GovAPI):

    def __init__(self, cfg):
        GovAPI.__init__(self)
        self.__cfg = cfg

    def _get_active(self,dict):
        return dict.get('active')

    def _get_id(self,dict):
        return dict.get('id')

    def _get_last_name(self,dict):
        return dict.get('lastName')

    def _get_first_name(self,dict):
        return dict.get('firstName')

    def _get_middle_name(self,dict):
        return ''

    def _get_party(self,dict):
        return dict.get('party')

    def _get_council(self,dict):
        return dict.get('council')

    def _get_gender(self,dict):
        return dict.get('gender')

    def _get_marital_status(self,dict):
        return dict.get('maritalStatus')

    def _get_birthdate(self,dict):
        return self._convert_utc_timestamp(dict.get('birthDate'))

    def _get_title(self,dict):
        return dict['salutationTitle']

    def _get_country(self,dict):
        return 'CH'

    def _get_state_postal_code(self,dict):
        return dict['cantonName']

    def _get_district(self,dict):
        return ''

    def _get_zip(self,dict):
        return dict.get('postalAddress').get('zip')

    def _get_town_name(self,dict):
        return dict.get('postalAddress').get('city')

    def _get_elected_date(self, dict):
        return self._convert_utc_timestamp(dict['councilMemberships'][0]['entryDate'])

    # http://ws-old.parlament.ch/councillors?format=json
    def load_government_members(self):
        page_number=1
        url = self.__cfg['govAPIUrl']
        politician_res = self.__cfg['govAPICouncillorsRes']
        par = self.__cfg['govAPIParams']
        while True:
            par[0]['pageNumber'] = str(page_number)
            headers = requests.utils.default_headers()
            headers.update({ 'User-Agent': 'Mozilla/5.0'})
            politicians = requests.get(url+politician_res, params=par[0], headers=headers).json()
            print("Requesting data from "+url+" (page: "+str(page_number)+")")
            has_more_pages = False
            for politician in politicians:
                if politician.get('hasMorePages'):
                    has_more_pages = True
                if politician['active']:
                    id = politician['id']
                    details = requests.get(url+politician_res+"/"+str(id), params=par[0], headers=headers).json()
                    #print(details)
                    self._add_person_record(details)
            if not has_more_pages:
                break
            else:
                page_number += 1
        return self._members
