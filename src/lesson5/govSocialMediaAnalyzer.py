import tweepy
import yaml
import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd

from tweepy import OAuthHandler
from pandas import DataFrame


from govAPIFactory import GovAPIFactory
from namematching import sort_words,normalize_unicode_to_ascii,double_metaphone


# A Social Media Analyzer class based on twitter
# anaylizing tweeter accounts of government members
# of a country.
class GovernmentSocialMediaAnalyzer(object):
    # Class Instance Variable
    __cfg = {}
    __country_code = None
    __tw_api = None
    __gov_api = None
    # Class Instance Variables used for the reporting
    __labels = None
    __col_screen_name = None
    __col_name = None
    __col_description = None
    __col_followers_count = None
    __col_friends_count = None
    __col_party = None
    # The merged data frame
    __merged_politican_df = None

    def __init__(self, country_code):
        self.__country_code = country_code

        # Dependent on the country parameter load the relevant configurations
        file_name = "config-"+country_code+".yaml"
        with open("../../cfg/"+file_name, 'r') as stream:
            try:
                self.__cfg= yaml.load(stream)
            except yaml.YAMLError as exc:
                print("Config File ", file_name, " wrong format", exc)
                exit(1)

        res = {}
        # Reading the secret values from a local disk
        with open("../../../secret/twitter.yaml", 'r') as stream:
            try:
                res= yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                exit(1)

        consumer_key = res['apiKey']
        consumer_secret = res['apiSecretKey']
        access_token = res['accessToken']
        access_token_secret = res['accessSecretToken']

        # attempt authentication
        try:
            # create OAuthHandler object
            auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.__tw_api = tweepy.API(auth)
        except:
            print("Error: Authentication Failed")
            exit(1)

        # Get an government api class instance for the country __country_code
        self.__gov_api = GovAPIFactory.create_country_gov_api(self.__country_code, self.__cfg)

        self.__extract_columns()

    def __extract_columns(self):
        accounts = self.__get_government_members()
        labels = range(0,len(accounts))
        self.__col_screen_name = [account.screen_name for account in accounts]
        self.__col_name = [account.name for account in accounts]
        self.__col_description = [account.description for account in accounts]
        self.__col_followers_count = [account.followers_count for account in accounts]
        self.__col_friends_count = [account.friends_count for account in accounts]
        # Exercise 1: Identify the Party
        self.__col_party = self.__check_for_party(accounts)

    def __get_government_members(self):
        lists = self.__tw_api.lists_all(self.__cfg['twitterListAccount'])
        for list in lists:
            if list.name == self.__cfg['twitterListName']:
                result = []
                for item in tweepy.Cursor(self.__tw_api.list_members, list_id=list.id).items():
                    result.append(item)
                return result
        return None

    # Method will return the party of the list member by analyzing
    # twitter account attributes. If party cannot be detected the
    # account column  have an entry "unknown"
    def __check_for_party(self, user_list):
        party_column = []
        # iterate through each user account
        for user in user_list:
            # iterate trough all parties
            for party in self.__cfg.get('parties'):
                res = "unknown"
                # Check first all abbreviations
                # We don't do lower here because that could result to false positive
                for abbr in party['abbrs']:
                    if abbr in user.description or abbr in user.screen_name:
                        res = party['abbrs'][0]
                        break
                # Check now if the party twitter screen name is referenced
                if res == "unknown":
                    if user.description is not None \
                            and party['twitter'] is not None \
                            and len(party['twitter']) > 0:
                        if party['twitter'].lower() in user.description.lower():
                            res = party['abbrs'][0]
                            break
                # Check now if a kewyword is referenced
                if res == "unknown":
                    if user.description is not None:
                        for keyword in party['keywords']:
                            if keyword.lower() in user.description.lower():
                                res = party['abbrs'][0]
                                break
                if res != "unknown":
                    break
            party_column.append(res)
        return party_column

    def create_tw_politican_table(self, apidef):
        # Panda Data Frame - Table of all Parliament Members
        panda_data = { 'ScreenName' : self.__col_screen_name,
                       'Name': self.__col_name,
                       'Description': self.__col_description,
                       "FollowersCount": self.__col_followers_count,
                       "FriendsCount": self.__col_friends_count,
                       "Party": self.__col_party
                       }
        df = DataFrame(panda_data, index=self.__labels)
        df = df.apply(self.__calculate_name_matching, axis=1)
        # Sort by Followers Count
        df = df.sort_values(['FollowersCount'], ascending=[0])
        # Create a Plotly Table
        trace = go.Table(
            header=dict(values=list(df.columns)),
            cells=dict(values=[df.ScreenName, df.Name, df.Description, df.FollowersCount, df.FriendsCount,
                               df.Party, df.col_match1, df.col_match2, df.col_match3]))
        data = [trace]
        py.plot(data, filename=self.__country_code+'-tw-politician-list')

        merge_df = pd.merge(left=df, right=apidef, how='left', left_on='col_match2', right_on='col_match2')

        trace = go.Table(
            header=dict(values=['ScreenName', 'Name', 'FollowersCount', 'FriendsCount', 'Party', 'party', 'electedDate',
                                'gender', 'maritalStatus', 'birthDate', 'normalizedName']),
            cells=dict(values=[merge_df.ScreenName, merge_df.Name, merge_df.FollowersCount, merge_df.FriendsCount,
                               merge_df.Party, merge_df.party, merge_df.electedDate, merge_df.gender,
                               merge_df.maritalStatus, merge_df.birthDate, merge_df.col_match1_x]))
        data = [trace]
        py.plot(data, filename=self.__country_code+'-tw-politician-merged-list')
        return merge_df

    def __calculate_name_matching(self, row):
        name = row['Name']
        for clean in self.__cfg['twitterNameCleaner']:
            name = name.replace(clean ,'')
        for expand in self.__cfg['twitterNamesExpander']:
            name = name.replace(expand.get('abbreviation'), expand.get('name'))
        norm_name = (sort_words(normalize_unicode_to_ascii(name))).strip()
        tp = double_metaphone(norm_name)
        row['col_match1'] = norm_name
        row['col_match2'] = tp[0]
        row['col_match3'] = tp[1]
        return row

    def create_tw_party_table(self, df):
        # Panda Data Frame - Table of Tweeter Users per Party
        # https://stackoverflow.com/questions/48909110/python-pandas-mean-and-sum-groupby-on-different-columns-at-the-same-time
        panda_data = { "Party": df.party,
                       "PartyCount": df.party, # Duplicate Party column for the counting
                       "FollowersCount": df.FollowersCount,
                       "FriendsCount": df.FriendsCount
                       }
        df = DataFrame(panda_data, index=self.__labels)
        df = df.fillna(0)
        # We use the as_index parameter, so that Party will also be a column of the data frame
        df = df.groupby(["Party"], as_index=False).agg({'PartyCount':'count','FollowersCount':'sum', 'FriendsCount': 'sum'})
        df = df.sort_values(['FollowersCount'], ascending=[0])
        print(df)
        # Create a Plotly Table
        trace = go.Table(
            header=dict(values=list(df.columns)),
            cells=dict(values=[df.Party,  df.PartyCount, df.FollowersCount, df.FriendsCount]))
        data = [trace]
        py.plot(data, filename=self.__country_code+'-tw-party-list')
        self.create_party_friends_count_bar_chart(df)
        self.create_party_politicans_count_pie_chart(df)

    def create_govapi_politican_table(self):
        df = self.__gov_api.create_politican_from_govapi_table()
        # Create a Plotly Table
        trace = go.Table(
            header = dict(values=list(df.columns)),
            cells = dict(values=list(df.values.transpose())))

        data = [trace]
        py.plot(data, filename=self.__country_code+'-govapi-member-list')
        return df

    # Charts
    def create_party_friends_count_bar_chart(self, df):
        data = [
            go.Bar(
                x=df.Party, # assign x as the dataframe column 'x'
                y=df.FriendsCount
            )
        ]
        py.plot(data, filename=self.__country_code+'-tw-party_politicans_count')

    def create_party_politicans_count_pie_chart(self, df):
        trace = go.Pie(labels=df.Party, values=df.PartyCount,
                       hoverinfo='label+percent', textinfo='value',
                       title="Twitter User per Party", titlefont=dict(
                family='Courier New, monospace',
                size=14,
                color='#7f7f7f'
            ))
        data = [trace]
        py.plot(data, filename=self.__country_code+'-tw-party_friends_count')