import tweepy
import yaml
import pandas as pd
import numpy as np
import plotly.plotly as py
import plotly.graph_objs as go

from tweepy import OAuthHandler
from textblob import TextBlob
# Own Modules
from text_cleaners import clean_text


# Generic Twitter Class for sentiment analysis.
class TwitterClient(object):

    def __init__(self):
        res = {}
        # Reading the secret values from a local disk
        with open("../../secret/twitter.yaml", 'r') as stream:
            try:
                res= yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        consumer_key = res['apiKey']
        consumer_secret = res['apiSecretKey']
        access_token = res['accessToken']
        access_token_secret = res['accessSecretToken']

        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.__api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")


    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(clean_text(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    def get_tweets(self, query, count = 10):
        '''
        Main function to fetch tweets and parse them.
        '''
        # empty list to store parsed tweets
        tweets = []

        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.__api.search(q = query, count = count)

            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                parsed_tweet = {}

                # saving text of tweet
                parsed_tweet['text'] = tweet.text
                # saving sentiment of tweet
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)

                parsed_tweet['favorite_count'] = tweet.favorite_count
                parsed_tweet['retweet_count'] =tweet.retweet_count
                parsed_tweet['hashtags']= tweet.entities["hashtags"]

                # appending parsed tweet to tweets list
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)

                # return parsed tweets
            return tweets

        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))

    def getMember(self):
        user = self.__api.get_user('SoMePolis')
        lists = self.__api.lists_all('SoMePolis')
        personList = None
        for list in lists:
            if list.name == 'BundesparlamentarierInnen':
                personList = list
        print(user)


def main():
    # creating object of TwitterClient Class
    api = TwitterClient()

    api.getMember()

    # calling function to get tweets
    tweets = api.get_tweets(query = 'from:cnn Trump', count = 200)



    # picking positive tweets from tweets
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    # percentage of positive tweets
    print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets)))
    # picking negative tweets from tweets
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    # percentage of negative tweets
    print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets)))
    # percentage of neutral tweets
    nt = len(tweets)-len(ntweets)-len(ptweets)
    print("Neutral tweets percentage: {} %".format(100*nt/len(tweets)))


    col1 = [tweet["sentiment"] for tweet in tweets]
    col2 = [tweet["favorite_count"] for tweet in tweets]
    col3 = [tweet["retweet_count"] for tweet in tweets]
    col4 = [tweet["hashtags"] for tweet in tweets]
    col5 = [tweet["text"] for tweet in tweets]
    labels = range(0,len(tweets))

    # Panda Data Set
    panda_data = { 'Sentiment' : col1,
                   'Favorite Count': col2,
                   'Retweet Count' : col3
                 }
    df = pd.DataFrame(panda_data , index=labels)
    print(df)

    # Plotly Table
    #trace = go.Table(
    #                 header=dict(values=['Sentiment','Favorite Count','Retweet Count','Hashtags','Text']),
    #                 cells=dict(values=[col1, col2, col3,col4,col5]))

    #data = [trace]
    #py.iplot(data, filename = 'basic_table')


    # printing first 5 positive tweets
    print("\n\nPositive tweets:")
    for tweet in ptweets[:10]:
        print(tweet['text'])

    # printing first 5 negative tweets
    print("\n\nNegative tweets:")
    for tweet in ntweets[:10]:
        print(tweet['text'])

if __name__ == "__main__":
    main()

