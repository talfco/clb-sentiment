import itertools
from namematching import doublemetaphone


class NameLookupDirectory:

    __lookup_dict = ({}, {})

    @classmethod
    def generate_combinations(cls,name_tuple):
        coms = []
        coms.append(name_tuple)
        i = len(list(name_tuple))-1
        while i > 0:
            coms.extend(itertools.combinations(name_tuple,i))
            i -=1
        return coms

    @classmethod
    def generate_normalized_name(cls, name_tuple):
        name_arr = list(name_tuple)
        name_arr.sort()
        name_str = ' '.join(name_tuple)
        return name_str.lower()

    def add_combinations_to_directory(self, comb_tuples, person_id):
        for comb in comb_tuples:
            concat_name = self.generate_normalized_name(comb)
            metaphone_tuple = doublemetaphone(concat_name)
            if metaphone_tuple[0] in self.__lookup_dict[0]:
                if not person_id in self.__lookup_dict[0][metaphone_tuple[0]]:
                    self.__lookup_dict[0][metaphone_tuple[0]].append(person_id)
            else:
                self.__lookup_dict[0][metaphone_tuple[0]] = [person_id]
            if metaphone_tuple[1] in self.__lookup_dict[1]:
                if not person_id in self.__lookup_dict[1][metaphone_tuple[1]]:
                    self.__lookup_dict[1][metaphone_tuple[1]].append(person_id)
            else:
                self.__lookup_dict[1][metaphone_tuple[1]] = [person_id]

    def add_person_to_lookup_directory(self, person_id, name_tuple):
        tuples = self.generate_combinations(name_tuple)
        self.add_combinations_to_directory(tuples, person_id)

    def match_name(self, name_tuple):
        match_list = []
        combinations = self.generate_combinations(name_tuple)
        for comb_tuple in combinations:
            concat_name = self.generate_normalized_name(comb_tuple)
            metaphone_tuple = doublemetaphone(concat_name)
            if metaphone_tuple[0] in self.__lookup_dict[0]:
                match_list.append((concat_name, self.__lookup_dict[0][metaphone_tuple[0]]))
        # Iterate through all matches and check for single result tuples
        # Ensure that the singe result tuples are pointing to the same id
        # If not or no single result tuple exists, return 'None'
        unique_id = None
        for match_tuple in match_list:
            if len(match_tuple[1]) == 1:
                if  unique_id is not None:
                    if unique_id != match_tuple[1][0]:
                        unique_id = None
                        break
                else:
                    unique_id = match_tuple[1][0]
        return unique_id, match_list
