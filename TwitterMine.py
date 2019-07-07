import tweepy
import csv
from imageai.Detection import ObjectDetection
import os
import urllib.request
import numpy as np
import requests
import io
from PIL import Image
consumer_key = "uqKb1h9prIwbAVCqocBuqInFs"
consumer_secret = "EXlWGr7VFTGJ00116M25mDWyNveORVkHVPGXHaAOsg1lwFUQn8"
access_token = "2388347288-uEH2UbQnr2uZYCZDuvh93wD8UHZ3PMB15diH9tK"
access_token_secret ="RCXSN3rj4m04ECekNo3DnF2u7B4G7AJauZXs3DmbX14dc"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

tweets = tweepy.Cursor(api.search,
                       q="gift",lang="en").items(1000);

file = open('user-id-targetTweet-PastTweets.csv', 'a', newline='')
writer = csv.writer(file)

statuses = tweepy.Cursor(api.user_timeline,
                             user_id="@wewweowew", tweet_mode="extended").items(15)

execution_path = os.getcwd()
detector = ObjectDetection()
detector.setModelTypeAsRetinaNet()
detector.setModelPath( os.path.join(execution_path , "resnet50_coco_best_v2.0.1.h5"))
detector.loadModel()

for status in statuses:
    if len(status.entities.get("media","")) != 0:
        imageList = status.entities.get("media","");
        imageurl = imageList[0].get("media_url","")
        with urllib.request.urlopen(imageurl) as url:
            q = urllib.request.urlretrieve(imageurl,"local-filename.jpg");
            detections = detector.detectObjectsFromImage(input_image=os.path.join(execution_path , "local-filename.jpg"), output_image_path=os.path.join(execution_path , "imagenew.jpg"))
            os.remove("imagenew.jpg")
            for eachObject in detections:
                print(eachObject["name"], " : ", eachObject["percentage_probability"])
            # I'm guessing this would output the html source code ?
        print(status);



for result in tweets:
    print(result)
    userid = result.user.id

    statuses = tweepy.Cursor(api.user_timeline,
                             user_id=result.user.id, tweet_mode="extended").items(5)

    csvRow = [result.user.screen_name, result.user.id, result.text]

    for status in statuses:
        if (not status.retweeted) and ('RT @' not in status.full_text) and (not status.in_reply_to_user_id)\
                and result.id != status.id and len(status.full_text.split()) >= 4:

            csvRow.append(status.full_text)

    writer.writerow(csvRow)

file.close()






