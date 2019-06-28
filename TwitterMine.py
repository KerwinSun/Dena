import tweepy
import csv

consumer_key = "uqKb1h9prIwbAVCqocBuqInFs"
consumer_secret = "EXlWGr7VFTGJ00116M25mDWyNveORVkHVPGXHaAOsg1lwFUQn8"
access_token = "2388347288-uEH2UbQnr2uZYCZDuvh93wD8UHZ3PMB15diH9tK"
access_token_secret ="RCXSN3rj4m04ECekNo3DnF2u7B4G7AJauZXs3DmbX14dc"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

tweets = tweepy.Cursor(api.search,
                       q="from:KerwinSUn1").items(1);

file = open('user-id-targetTweet-PastTweets.csv', 'a', newline='')
writer = csv.writer(file)

for result in tweets:
    print(result)
    userid = result.user.id

    statuses = tweepy.Cursor(api.user_timeline,
                             user_id=result.user.id, tweet_mode="extended").items(10)

    csvRow = [result.user.screen_name, result.user.id, result.text]

    for status in statuses:
        if (not status.retweeted) and ('RT @' not in status.full_text) and (not status.in_reply_to_user_id)\
                and result.id != status.id and len(status.full_text.split()) >= 4:

            csvRow.append(status.full_text)

    writer.writerow(csvRow)

file.close()






