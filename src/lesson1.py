import tweepy
import yaml
import plotly

from tweepy import OAuthHandler
from pandas import DataFrame


# Generic Twitter Class for sentiment analysis.
# https://twitter.com/SoMePolis
class TwitterClient(object):


    def __init__(self):
        res = {}
        # Reading the secret values from a local disk
        with open("../../secret/twitter.yaml", 'r') as stream:
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
            self.__api = tweepy.API(auth)
        except:
            print("Error: Authentication Failed")
            exit(1)

    def get_government_members(self):
        lists = self.__api.lists_all('SoMePolis')

        for list in lists:
            if list.name == 'BundesparlamentarierInnen':
                result = []
                for item in tweepy.Cursor(self.__api.list_members, list_id=list.id).items():
                    result.append(item)
                return result
        return None


    def create_plotly_table(self):
        lists = self.get_government_members()
        labels = range(0,len(lists))
        col1 = [list.screen_name for list in lists]
        col2 = [list.name for list in lists]
        col3 = [list.description for list in lists]
        col4 = [list.followers_count for list in lists]
        col5 = [list.friends_count for list in lists]

        # Panda Data Set
        panda_data = { 'ScreenName' : col1,
                       'Name': col2,
                       'Description': col3,
                       "FollowersCount": col4,
                       "FriendsCount": col5
                    }
        df = DataFrame(panda_data , index=labels)

        trace = plotly.graph_objs.Table(
        header = dict(values=list(df.columns)),
        cells = dict(values=[df.ScreenName, df.Name, df.Description, df.FollowersCount, df.FriendsCount]))
        data = [trace]
        plotly.plotly.iplot(data, filename='pandas_table')


def main():
    api = TwitterClient()
    api.create_plotly_table()


if __name__ == '__main__':
    main()
