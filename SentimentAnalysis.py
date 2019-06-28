import csv
import ibm_watson

from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, CategoriesOptions, SentimentOptions

service = NaturalLanguageUnderstandingV1(
    version='2018-03-16',
    url='https://gateway.watsonplatform.net/natural-language-understanding/api',
    iam_apikey='3lu4pe1GCX_ey2JIq5fTh5MjccYo0peTs8PgUCOW6Jw8')


file = open('user-id-targetTweet-PastTweets.csv', 'r', newline='')
targetfile = open('user-id-target_entity+sentiment', 'a', newline='')
featurefile = open('user-id-feature_entity+sentiment', 'a', newline='')
targetwriter = csv.writer(targetfile)
featurewriter = csv.writer(featurefile)

reader = csv.reader(file)
big_list = list(reader)

for row in big_list:

    twitter_screen_name = row[0];
    twitter_id = row[1]
    target_tweet = row[2]
    csvRow = [twitter_screen_name, twitter_id]

    try:
        response = service.analyze(
            text=target_tweet,
            features=Features(sentiment=SentimentOptions(),
                              keywords=KeywordsOptions()
                              )
        ).get_result()

        for keyword in response['keywords']:
            csvRow.append(keyword['text'] + ":" + str(response['sentiment']['document']['score']))

        targetwriter.writerow(csvRow)

    except:
        print("tweet malformed")

    csvRow = [twitter_screen_name, twitter_id]

    for past_tweet in row[3:]:

        response = service.analyze(
            text=past_tweet,
            features=Features(sentiment=SentimentOptions(), keywords=KeywordsOptions())
        ).get_result()

        print(past_tweet)
        print(response)

        for keyword in response['keywords']:
            csvRow.append(keyword['text'] + ":" + str(response['sentiment']['document']['score']))


        # sentiment analysis here

    featurewriter.writerow(csvRow)

targetfile.close()
featurefile.close()
file.close()






