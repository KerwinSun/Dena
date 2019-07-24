import csv
import ibm_watson
import spacy
from TaxonomySearcher import TaxonomySearcher

from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, CategoriesOptions, SentimentOptions
from textblob import TextBlob
from textblob.np_extractors import ConllExtractor

"""""
service = NaturalLanguageUnderstandingV1(
    version='2019-07-12',
    url='https://gateway.watsonplatform.net/natural-language-understanding/api',
    iam_apikey='llOUos0uFvX9rCvN-4eNUx4GJdDH8WrSMW6fOBmzOLdQ')
"""

file = open('user-id-targetTweet-PastTweets.csv', 'r', newline='', encoding="utf-8")
featurefile = open('user-id-feature_entity+sentiment.csv', 'a', newline='', encoding="utf-8")
featurewriter = csv.writer(featurefile)
searcher = TaxonomySearcher()
npl = spacy.load("en_core_web_lg")

reader = csv.reader(file)
big_list = list(reader)
good_labels = ["PERSON", "FACILITY", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "WORK OF ART", "LANGUAGE"]

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
            if target['relevance'] > 0.5 and searcher.searchTaxMap(target['text'].lower()) \
                    and target['text'].lower() != "gift":
                targets.append(target['text'].lower())

    except Exception as e:
        print(e)

    try:
        doc = npl(target_tweet)

        for entity in doc.ents:
            if entity.label_ in good_labels:
                print("named: " + entity.text + " | label: " + entity.label_)
                targets.append(entity.text)

    except Exception as e:
        print(e)

    entityDict = {}

    for past_tweet in row[3:]:

        try:
            response = service.analyze(
                text=past_tweet,
                features=Features(sentiment=SentimentOptions(),
                                  keywords=KeywordsOptions(), categories=CategoriesOptions() )
            ).get_result()

            for keyword in response['keywords']:

                if keyword['text'].lower() in entityDict:
                    entityDict[keyword['text'].lower()] += response['sentiment']['document']['score']
                else:
                    entityDict[keyword['text'].lower()] = response['sentiment']['document']['score']

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






