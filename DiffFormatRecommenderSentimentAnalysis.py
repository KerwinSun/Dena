import csv
import urllib.request
import os
import tweepy
from imageai.Detection import ObjectDetection
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, CategoriesOptions, SentimentOptions
from textblob import TextBlob
from spacy.pipeline import EntityRuler
import spacy
from TaxonomySearcher import TaxonomySearcher

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
api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
tweets = tweepy.Cursor(api.search,
                       q="gift",lang="en",result_type='mixed').items(100);
execution_path = os.getcwd()
detector = ObjectDetection()
detector.setModelTypeAsRetinaNet()
detector.setModelPath( os.path.join(execution_path , "resnet50_coco_best_v2.0.1.h5"))
detector.loadModel()
searcher = TaxonomySearcher();
nlp = spacy.load("en_core_web_lg")
count = 0
good_labels = ["PERSON", "FACILITY", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "WORK OF ART", "LANGUAGE"]

def deEmojify(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')


userId = set();
i = 0


def addDataRow(userid,item,rating,csvwriter):
    csvrow = [userid,item,rating]
    csvwriter.writerow(csvrow)


for result in tweets:

    if result.user.id in userId:
        continue
    else:
        userId.add(result.user.id)

    statuses = tweepy.Cursor(api.user_timeline,
                             user_id=result.user.id, tweet_mode="extended").items(5)
    csvRow3 = []
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
                doc = nlp("u"+deEmojify(status.full_text));
                # sentiment analysis here
                for keyword in response['keywords']:
                    if searcher.searchTaxMap(keyword['text'].lower()):
                            addDataRow(i, keyword['text'], response['sentiment']['document']['score'], writer)

                for ent in doc.ents:
                    if ent.label_ in good_labels:
                        try:
                            print("Entity:" + ent.text + ent.label_)
                            addDataRow(i, keyword['text'], response['sentiment']['document']['score'], writer)
                        except:
                            print("Entity:" + ent.text+ent.label_)
                            addDataRow(i, keyword['text'], response['sentiment']['document']['score'], writer)

                if len(status.entities.get("media", "")) != 0:
                    imageList = status.entities.get("media", "");
                    imageurl = imageList[0].get("media_url", "")
                    with urllib.request.urlopen(imageurl) as url:
                        q = urllib.request.urlretrieve(imageurl, "local-filename.jpg");
                        detections = detector.detectObjectsFromImage(
                            input_image=os.path.join(execution_path, "local-filename.jpg"),
                            output_image_path=os.path.join(execution_path, "imagenew.jpg"))
                        os.remove("imagenew.jpg")
                        os.remove("local-filename.jpg")
                        for eachObject in detections:
                            if searcher.searchTaxMap(keyword['text']):
                                try:
                                    addDataRow(i, keyword['text'], response['sentiment']['document']['score'], writer)
                                except:
                                    addDataRow(i, keyword['text'], response['sentiment']['document']['score'], writer)
            except:
                response = {};
                print("tweet has unsupported languages")
    i += 1

writefile.close()
file.close()



