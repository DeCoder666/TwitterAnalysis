from flask import Flask, render_template, request, redirect
from flask_bootstrap import Bootstrap
from database import *
import requests, json, random, tweepy
import pandas as pd
from textblob import TextBlob
#from wordcloud import WordCloud
from styleformer import Styleformer
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yes'



#API configuration
api_key = "PQrpOG29M8xjgra5L6Kid5okR"
api_key_secret = "UW4CF31wXC5oG1E65GRGYM23s0wGcIdsBl6pqZLS9wIOvojBqi"

access_token = "1314088972147134465-yPvrcbIjtrQYDCOWlDf52aNgJAV1Tt"
access_token_secret = "IzHd7M2EaBmNl2P1c5LELgEEfhsaWcim4ZFbjPdSGnSAt"

auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


#Route to tweet styleformer
@app.route("/rewrite", methods=['GET', 'POST'])
def rewrite():
    if request.method == 'GET':
        return render_template('rewrite.html')
    else:
        url = request.form['profile-url']
        
        uid = url.replace('https://twitter.com/','')
        tweets = []
        likes = []
        sentiments = []
        tweet_subjectivity = []
        
        #Going over tweets and extracting data
        numberOfTweets = request.form['numtweets']
        for i in tweepy.Cursor(api.user_timeline, id=uid, tweet_mode="extended").items(int(numberOfTweets)):
            tweets.append(i.full_text)
            g = TextBlob(i.full_text)
            sub = g.sentiment.subjectivity
            g = g.sentiment.polarity
            sentiments.append(g)
            tweet_subjectivity.append(sub)
            print(TextBlob(i.full_text).sentiment.polarity)
            likes.append(i.favorite_count)
            username = i.user.name
            u = "https://twitter.com/twitter/statuses/" + str(i.id)
        
        randomTweet = tweets[random.randint(1,len(tweets))-1]
        
        #Casual to formal
        sf = Styleformer(style=0)
        newTweetFormal = sf.transfer(randomTweet)
        
        #ActivetoPassive
        sf1 = Styleformer(style=2)
        newTweetPassive = sf1.transfer(randomTweet)
        
        #Formal to casual
        sf2 = Styleformer(style=1)
        newTweetCasual = sf2.transfer(randomTweet)
        
        return render_template('rewrite.html',randomTweet = randomTweet, newTweetFormal = newTweetFormal,
                               newTweetPassive = newTweetPassive, newTweetCasual=newTweetCasual)
        
            
        

#Route to Profile Analyzer
@app.route("/", methods=['GET', 'POST'])
def twitterSentiment():
    if request.method == 'GET':
        return render_template("sentiment.html")
    else:
        #Getting the Twitter User ID
        url = request.form['profile-url']
        
        uid = url.replace('https://twitter.com/','')
        
        tweets = []
        likes = []
        sentiments = []
        tweet_subjectivity = []
        
        #Going over tweets and extracting data
        numberOfTweets = request.form['numtweets']
        for i in tweepy.Cursor(api.user_timeline, id=uid, tweet_mode="extended").items(int(numberOfTweets)):
            tweets.append(i.full_text)
            g = TextBlob(i.full_text)
            sub = g.sentiment.subjectivity
            g = g.sentiment.polarity
            sentiments.append(g)
            tweet_subjectivity.append(sub)
            print(TextBlob(i.full_text).sentiment.polarity)
            likes.append(i.favorite_count)
            username = i.user.name
            u = "https://twitter.com/twitter/statuses/" + str(i.id)
        
        sentimentNegative = 0
        sentimentNeutral = 0
        sentimentPositive = 0
        
        #Calculating the amount of different types tweets by their polarity
        for s in sentiments:
            if s <= -0.1:
                sentimentNegative+=1
            elif s > -0.1 and s < 0.1:
                sentimentNeutral+=1
            elif s >= 0.1:
                sentimentPositive+=1
        
        #Calculating average subjectivity of tweets
        subjectivityTotal = 0
        for s1 in tweet_subjectivity:
            subjectivityTotal+=s1
        
        subjectivityAverage = subjectivityTotal/len(tweets)
        
        #Rendering the page
        return render_template('sentiment.html', 
#                               tweet1 = df,formal = dformal, sentiment1 = sentiment2.sentiment
                               tweetUrl = u, username1 = username,
                               sentimentNegative = sentimentNegative, sentimentNeutral = sentimentNeutral,
                              sentimentPositive = sentimentPositive, numoftweets = len(tweets), subjectivityAverage = subjectivityAverage)

if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
