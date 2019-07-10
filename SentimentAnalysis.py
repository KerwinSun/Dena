import csv
import ibm_watson
from TaxonomySearcher import TaxonomySearcher

from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, CategoriesOptions, SentimentOptions

service = NaturalLanguageUnderstandingV1(
    version='2018-03-16',
    url='https://gateway.watsonplatform.net/natural-language-understanding/api',
    iam_apikey='3lu4pe1GCX_ey2JIq5fTh5MjccYo0peTs8PgUCOW6Jw8')


file = open('user-id-targetTweet-PastTweets.csv', 'r', newline='', encoding="utf-8")
featurefile = open('user-id-feature_entity+sentiment.csv', 'a', newline='', encoding="utf-8")
featurewriter = csv.writer(featurefile)
searcher = TaxonomySearcher()

reader = csv.reader(file)
big_list = list(reader)


for row in big_list:

    twitter_screen_name = row[0]
    twitter_id = row[1]
    target_tweet = row[2]
    csvRow = [twitter_screen_name, twitter_id]
    targets = []

    try:
        response = service.analyze(
            text=target_tweet,
            features=Features(sentiment=SentimentOptions(),
                              keywords=KeywordsOptions(),
                              categories=CategoriesOptions()
                              )
        ).get_result()

        print(response)
        csvRow.append(" ")

        for target in response['keywords']:
            if target['relevance'] > 0.5:
                if searcher.searchTaxMap(target['text']):
                    targets.append(target['text'])

    except Exception as e:
        print("hi")

    entityDict = {}

    for past_tweet in row[3:]:

        try:
            response = service.analyze(
                text=past_tweet,
                features=Features(sentiment=SentimentOptions(),
                                  keywords=KeywordsOptions(), categories=CategoriesOptions() )
            ).get_result()

            for keyword in response['keywords']:

                if keyword['text'] in entityDict:
                    entityDict[keyword['text']] += response['sentiment']['document']['score']
                else:
                    entityDict[keyword['text']] = response['sentiment']['document']['score']

            # sentiment analysis here

        except Exception as e:
            print(e)

    numFeatures = 5

    for x in range(numFeatures):

        if len(entityDict) == 0:
            break

        mostLikedEntity = (max(entityDict, key=entityDict.get))
        csvRow.append(mostLikedEntity)
        entityDict.pop(mostLikedEntity)

    for target in targets:
        csvRow[2] = target
        featurewriter.writerow(csvRow)

featurefile.close()
file.close()






