import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from twitter import Api
from nltk.corpus import stopwords
import httplib
 
class TwitterClient(object):
    

    def __init__(self):

        # keys and tokens from the Twitter Dev Console
        consumer_key = '5a1tL5vH7qJ5k8btGtjFsziQb'
        consumer_secret = 'FC5nqWXQkJVKs1fmrb5InuDe0T7RE2H2FBWcqnoWNZXUZRe0lz'
        access_token = '1329456000-xxF6gN0EtV3kJueCWIagMEehqU1CNztcXFo0WlD'
        access_token_secret = 'mzCMqkWOLtOaWvQ1CRf8YztDgWCnfSKmXFaSa3VBXKqMY'
        api = Api(consumer_key, consumer_secret, access_token, access_token_secret)
        
        def preprocess(tweet, ascii=True, ignore_rt_char=True, ignore_url=True, ignore_mention=True, ignore_hashtag=True,letter_only=True, remove_stopwords=True, min_tweet_len=3):
            sword = stopwords.words('english')

            if ascii:  # maybe remove lines with ANY non-ascii character
                for c in tweet:
                    if not (0 < ord(c) < 127):
                        return ''

            tokens = tweet.lower().split()  # to lower, split
            res = []

            for token in tokens:
                if remove_stopwords and token in sword: # ignore stopword
                    continue
                if ignore_rt_char and token == 'rt': # ignore 'retweet' symbol
                    continue
                if ignore_url and token.startswith('https:'): # ignore url
                    continue
                if ignore_mention and token.startswith('@'): # ignore mentions
                    continue
                if ignore_hashtag and token.startswith('#'): # ignore hashtags
                    continue
                if letter_only: # ignore digits
                    if not token.isalpha():
                        continue
                elif token.isdigit(): # otherwise unify digits
                    token = '<num>'

                res += token, # append token

            if min_tweet_len and len(res) < min_tweet_len: # ignore tweets few than n tokens
                return ''
            else:
                return ' '.join(res)
        
        for line in api.GetStreamSample():
            if 'text' in line and line['lang'] == u'en': # step 1
                text = line['text'].encode('utf-8').replace('\n', ' ') # step 2
                p_t = preprocess(text)

        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")
 
    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
 
    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
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
            fetched_tweets = self.api.search(q = query, count = count)
 
            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                parsed_tweet = {}
 
                # saving text of tweet
                parsed_tweet['text'] = tweet.text
                # saving sentiment of tweet
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)
 
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

def get_tfidf(tweet_list, top_n, max_features=5000):
        """ return the top n feature names and idf scores of a tweets list """
        tfidf_vectorizer = TfidfVectorizer(max_features=max_features)
        tfidf_vectorizer.fit_transform(tweet_list)
        indices = np.argsort(tfidf_vectorizer.idf_)[::-1]
        features = tfidf_vectorizer.get_feature_names()
        top_feature_name = [features[i] for i in indices[:top_n]]
        top_feautre_idf = tfidf_vectorizer.idf_[indices][:top_n]
        return top_feature_name, top_feautre_idf
 
def main():
    # creating object of TwitterClient Class
    api = TwitterClient()
    # calling function to get tweets
    tweets = api.get_tweets(query = 'Exxon Mobil', count = 200)
 
    # picking positive tweets from tweets
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    # percentage of positive tweets
    print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets)))
    # picking negative tweets from tweets
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    # percentage of negative tweets
    print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets)))
    # percentage of neutral tweets
    print("Neutral tweets percentage: {} %".format(100*(len(tweets) - len(ntweets) - len(ptweets))/int(len(tweets))))
 
    # printing first 5 positive tweets
    print("\n\nPositive tweets:")
    for tweet in ptweets[:10]:
        print(tweet['text'].encode('utf-8'))
    
    print ("\n\n")
    print("\n\nNegative tweets:")
    for tweet in ntweets[:10]:
        print(tweet['text'].encode('utf-8'))
    
        clean = clean_tweet(tweet)
        print(type(clean))
 
      
#
if __name__ == "__main__":
    # calling main function
    main()


    