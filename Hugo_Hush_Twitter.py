# Hugo Hush Twitter Bot
# Tweepy Documentation: http://docs.tweepy.org/en/v3.8.0/index.html
# Youtube tutorial: https://www.youtube.com/watch?v=ewq-91-e2fw

import tweepy
import json
import random
import time
import config
from datetime import datetime

auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

date_format = "%Y-%m-%d %H:%M:%S"
print("Running bot ...")

while True:
    did_tweet = False 

    # Get an list of replies and the last replies that were sent
    with open("Reply_Data.json", "r") as fp:
        reply_data = json.load(fp)
        last_replies = reply_data["last_replies"]
        reply_dates = reply_data["reply_dates"]
        replies = reply_data["replies"]

    # Get a user and the date of the last reply to him 
    for user, reply_date_str in reply_dates.items():

        # Get a response that wasn't used recently
        while reply := random.choice(replies):
            if reply not in last_replies:
                break

        # Get the latest tweets from the user
        public_tweets = api.user_timeline(user, count=5)

        for user_tweet in public_tweets:

            # Don't reply to a retweet or reply
            user_tweet_is_retweet = hasattr(user_tweet, "retweeted_status")
            user_tweet_is_reply = user_tweet.in_reply_to_status_id 
            if user_tweet_is_retweet or user_tweet_is_reply: 
                continue

            # Don't reply if this tweet is older than the last reply to this user
            last_reply_date = datetime.strptime(reply_date_str, date_format).date()
            user_tweet_date = user_tweet.created_at.date()
            if last_reply_date >= user_tweet_date:
                continue

            print("Attempt reply to ", user)
            print(user_tweet.text)

            # Reply and save the data if successful
            reply_to_user = reply.replace("@someone", "@"+user)
            try:
                api.update_status(reply_to_user, in_reply_to_status_id=user_tweet.id_str)
            except tweepy.TweepError as e:
                print("Error:\n", e)
            else:
                did_tweet = True
                reply_dates[user] = user_tweet.created_at.strftime(date_format)
                last_replies.append(reply)
                last_replies.pop(0)
                print("Replied Successfully")
            
            time.sleep(3*60)
            break

    # Save the time of each new reply
    if did_tweet:
        reply_data["reply_dates"] = reply_dates
        reply_data["last_replies"] = last_replies
        with open("Reply_Data.json", "w") as fp:
           json.dump(reply_data, fp, indent = 3)
    
    time.sleep(5*60)
    


