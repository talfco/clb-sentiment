from abc import ABC, abstractmethod
from pandas import DataFrame
import datetime
from namematching import sort_words,normalize_unicode_to_ascii,double_metaphone


class GovAPI(ABC):

    _members = []

    # The method will load all government members into the members table
    # It will do that by calling the method 'add_person_record()'
    @abstractmethod
    def load_government_members(self):
        pass

    # These getters must be implemented by the specific class which inherits
    # from this one. These are the mapping rules to get the data out of the
    # gov api dictionary structure to our ones
    @abstractmethod
    def _get_active(self,dict):
        pass

    @abstractmethod
    def _get_id(self,dict):
        pass

    @abstractmethod
    def _get_last_name(self,dict):
        pass

    @abstractmethod
    def _get_first_name(self,dict):
        pass

    def _get_middle_name(self,dict):
        pass

    def _get_party(self,dict):
        return ''

    def _get_council(self,dict):
        return ''

    def _get_gender(self,dict):
        return ''

    def _get_marital_status(self,dict):
        return ''

    def _get_birthdate(self,dict):
        return ''

    def _get_title(self,dict):
            return ''

    def _get_country(self,dict):
        return ''

    def _get_state_postal_code(self,dict):
        return ''

    def _get_district(self,dict):
        return ''

    def _get_zip(self,dict):
        return ''

    def _get_town_name(self,dict):
        return ''

    def _get_elected_date(self, dict):
        return ''

    # This method will add a normalized person
    # record to our members array
    def _add_person_record(self, dict):
        person = {
            'id': self._get_id(dict),
            'active': self._get_active(dict),
            'lastName': self._get_last_name(dict),
            'firstName': self._get_first_name(dict),
            'middleName':self._get_middle_name(dict),
            'gender': self._get_gender(dict),
            'party': self._get_party(dict),
            'council' : self._get_council(dict),
            'electedDate': self._get_elected_date(dict),
            'birthDate': self._get_birthdate(dict),
            'maritalStatus': self._get_marital_status(dict),
            'title':  self._get_title(dict),
            'statePostalCode': self._get_state_postal_code(dict),
            'district': self._get_district(dict),
            'zip': self._get_zip(dict),
            'townName': self._get_town_name(dict)
        }
        self._members.append(person)

    def create_politican_from_govapi_table(self):
        self.load_government_members()
        df = DataFrame.from_records(self._members)
        df = df.apply(self.__calculate_name_matching, axis=1)
        return df

    # We add three additional rows required for the fuzzy
    # name matching
    def __calculate_name_matching(self, row):
        name = row['lastName']+' '+row['firstName']+' '+row['middleName']
        norm_name = (sort_words(normalize_unicode_to_ascii(name))).strip()
        tp = double_metaphone(norm_name)
        row['col_match1'] = norm_name
        row['col_match2'] = tp[0]
        row['col_match3'] = tp[1]
        return row

    # Helper Function to convert a date to a UTC date
    def _convert_utc_timestamp(self, edate):
        if edate is None:
            return None
        d = datetime.datetime.strptime(edate, '%Y-%m-%dT%H:%M:%SZ')
        return d.strftime("%d.%m.%Y")