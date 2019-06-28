import csv
import ibm_watson

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

for row in big_list:

    twitter_screen_name = row[0];
    twitter_id = row[1]
    target_tweet = row[2]
    csvRow = [twitter_screen_name, twitter_id]
    csvRow2 = [""]
    csvRow3 = [""]
    try:
        response = service.analyze(
            text=target_tweet,
            features=Features(sentiment=SentimentOptions(),
                              categories=CategoriesOptions()
                              )
        ).get_result()

        for key in response: print(key)
        csvRow.append(response['categories'][0]['label'])

    except:
        response = {}
        print("tweet malformed")

    for past_tweet in row[3:]:

        response = service.analyze(
            text=past_tweet,
            features=Features(sentiment=SentimentOptions(), categories=CategoriesOptions(), keywords = KeywordsOptions())
        ).get_result()

        print(past_tweet)
        print(response)

        # sentiment analysis here
        for keyword in response['keywords']:
            csvRow2.append(keyword['text']);

    csvRow3;
    for past_tweet in row[3:]:
        response = service.analyze(
            text=past_tweet,
            features=Features(sentiment=SentimentOptions(), categories=CategoriesOptions(), keywords=KeywordsOptions())
        ).get_result()
        for keyword in response['keywords']:
            index = csvRow2.index(keyword['text'])
            csvRow3.insert(index,response['sentiment']['document']['score'])

writer.writerow(csvRow2)
writer.writerow(csvRow3)
writefile.close()
file.close()
print(csvRow2)
print(csvRow3)



