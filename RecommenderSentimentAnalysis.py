import csv
import ibm_watson
import urllib.request
import numpy as np
import requests
import io
import os
import tweepy
from PIL import Image
from imageai.Detection import ObjectDetection
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, CategoriesOptions, SentimentOptions

service = NaturalLanguageUnderstandingV1(
    version='2018-03-16',
    url='https://gateway.watsonplatform.net/natural-language-understanding/api',
    iam_apikey='3lu4pe1GCX_ey2JIq5fTh5MjccYo0peTs8PgUCOW6Jw8')


file = open('user-id-targetTweet-PastTweets.csv', 'r', newline='')
writefile = open('user-id-sentiment-category_and_score', 'a', newline='')
writer = csv.writer(writefile)

reader = csv.reader(file)
big_list = list(reader)
csvRow2 = [""]
csvRow3 = [""]
consumer_key = "uqKb1h9prIwbAVCqocBuqInFs"
consumer_secret = "EXlWGr7VFTGJ00116M25mDWyNveORVkHVPGXHaAOsg1lwFUQn8"
access_token = "2388347288-uEH2UbQnr2uZYCZDuvh93wD8UHZ3PMB15diH9tK"
access_token_secret ="RCXSN3rj4m04ECekNo3DnF2u7B4G7AJauZXs3DmbX14dc"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

tweets = tweepy.Cursor(api.search,
                       q="wewweowew",lang="en").items(5);



execution_path = os.getcwd()
detector = ObjectDetection()
detector.setModelTypeAsRetinaNet()
detector.setModelPath( os.path.join(execution_path , "resnet50_coco_best_v2.0.1.h5"))
detector.loadModel()


for result in tweets:
    statuses = tweepy.Cursor(api.user_timeline,
                             user_id=result.user.id, tweet_mode="extended").items(5)
    for status in statuses:
        if (not status.retweeted) and ('RT @' not in status.full_text) and (not status.in_reply_to_user_id)\
                and result.id != status.id:
            try:
                response = service.analyze(
                    text=status.full_text,
                    features=Features(sentiment=SentimentOptions(), categories=CategoriesOptions(),
                                      keywords=KeywordsOptions())
                ).get_result()
                print(status.full_text)
                print(response)
                # sentiment analysis here
                for keyword in response['keywords']:
                    csvRow2.append(keyword['text']);
                    index = csvRow2.index(keyword['text'])
                    score = response['sentiment']['document']['score'];
                    csvRow3.insert(index, score)

                if len(status.entities.get("media", "")) != 0:
                    imageList = status.entities.get("media", "");
                    imageurl = imageList[0].get("media_url", "")
                    with urllib.request.urlopen(imageurl) as url:
                        q = urllib.request.urlretrieve(imageurl, "local-filename.jpg");
                        detections = detector.detectObjectsFromImage(
                            input_image=os.path.join(execution_path, "local-filename.jpg"),
                            output_image_path=os.path.join(execution_path, "imagenew.jpg"))
                        os.remove("imagenew.jpg")
                        for eachObject in detections:
                            csvRow2.append(eachObject["name"]);
                            index = csvRow2.index(keyword['text'])
                            csvRow3.insert(index, score)

                writer.writerow(csvRow3)
            except:
                response = {};
                print("tweet has unsupported languages")





# for row in big_list:
#     twitter_screen_name = row[0];
#     twitter_id = row[1]
#     target_tweet = row[2]
#     csvRow = [twitter_screen_name, twitter_id]
#     csvRow3 = [""] * len(csvRow2)
#     try:
#         response = service.analyze(
#             text=target_tweet,
#             features=Features(sentiment=SentimentOptions(),
#                               categories=CategoriesOptions()
#                               )
#         ).get_result()
#
#         for key in response: print(key)
#         csvRow.append(response['categories'][0]['label'])
#
#     except:
#         response = {}
#         print("tweet malformed")
#
#     for past_tweet in row[3:]:
#
#         try:
#             response = service.analyze(
#             text=past_tweet,
#             features=Features(sentiment=SentimentOptions(), categories=CategoriesOptions(), keywords = KeywordsOptions())
#         ).get_result()
#             print(past_tweet)
#             print(response)
#             # sentiment analysis here
#             for keyword in response['keywords']:
#                 csvRow2.append(keyword['text']);
#                 index = csvRow2.index(keyword['text'])
#                 score = response['sentiment']['document']['score'];
#                 csvRow3.insert(index, score)
#
#             if len(past_tweet.entities.get("media", "")) != 0:
#                 imageList = past_tweet.entities.get("media", "");
#                 imageurl = imageList[0].get("media_url", "")
#                 with urllib.request.urlopen(imageurl) as url:
#                     q = urllib.request.urlretrieve(imageurl, "local-filename.jpg");
#                     detections = detector.detectObjectsFromImage(
#                         input_image=os.path.join(execution_path, "local-filename.jpg"),
#                         output_image_path=os.path.join(execution_path, "imagenew.jpg"))
#                     os.remove("imagenew.jpg")
#                     for eachObject in detections:
#                         csvRow2.append(eachObject["name"]);
#                         index = csvRow2.index(keyword['text'])
#                         csvRow3.insert(index, score)
#
#             writer.writerow(csvRow3)
#         except:
#             response = {};
#             print("tweet has unsupported languages")

writer.writerow(csvRow2)
#writer.writerow(csvRow3)
writefile.close()
file.close()
print(csvRow2)
print(csvRow3)



