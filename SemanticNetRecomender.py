import tweepy
import csv
import spacy
from TaxonomySearcher import TaxonomySearcher
from textblob import TextBlob
from textblob.np_extractors import ConllExtractor
from textblob.taggers import NLTKTagger
from textblob.wordnet import Synset
from textblob import Word
import string

consumer_key = "uqKb1h9prIwbAVCqocBuqInFs"
consumer_secret = "EXlWGr7VFTGJ00116M25mDWyNveORVkHVPGXHaAOsg1lwFUQn8"
access_token = "2388347288-uEH2UbQnr2uZYCZDuvh93wD8UHZ3PMB15diH9tK"
access_token_secret ="RCXSN3rj4m04ECekNo3DnF2u7B4G7AJauZXs3DmbX14dc"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


extractor = ConllExtractor()
nltk_tagger = NLTKTagger()
searcher = TaxonomySearcher()
npl = spacy.load("en_core_web_lg")

good_labels = ["PERSON", "FACILITY", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "WORK OF ART", "LANGUAGE"]
good_PoS_Tags = ["NN", "NNS", "NNP", "NNPS"]

file = open('TaxonomyUserTarget.csv', 'a', newline='', encoding="utf-8")
writer = csv.writer(file)


user = api.get_user("KerwinSUn1")
print(user)
userid = user.id

# helper methods to assist in sanitising tweets before analysis
def clean(inputString):
    printable = set(string.printable)
    filter(lambda x: x in printable, inputString)
    return inputString.encode('ascii', 'ignore').decode('ascii')

statuses = api.user_timeline(
    user_id=userid, include_rts=False, exclude_replies=True, tweet_mode="extended")

csvRow = [user.screen_name, user.id]

for status in statuses:
    if True:
        csvRow.append(clean(status.full_text))

try:
    print(csvRow)
    writer.writerow(csvRow)

except Exception as e:

    print(e)

file.close()
# recommendation starts here

entityDict = {}

for status in statuses:

    print("TWEET :" + status.full_text)
    target_tweet = status.full_text
    blob = TextBlob(target_tweet, pos_tagger=nltk_tagger)

    # get categorical keywords
    try:
        keywords = blob.pos_tags

        for taggedTuple in keywords:

            keyword = taggedTuple[0]
            tag = taggedTuple[1]

            if tag in good_PoS_Tags:

                print(keyword + "::" + tag)

                if searcher.searchTaxMap(keyword.lower()) and keyword.lower() != "gift" :

                    if keyword.lower() in entityDict:
                        entityDict[keyword.lower()] += blob.sentiment.polarity
                    else:
                        entityDict[keyword.lower()] = blob.sentiment.polarity

    except Exception as e:
        print(e)

    # get named nouns
    try:
        doc = npl(target_tweet)

        for entity in doc.ents:
            if entity.label_ in good_labels:

                if keyword.lower() in entityDict:
                    entityDict[keyword.lower()] += blob.sentiment.polarity
                else:
                    entityDict[keyword.lower()] = blob.sentiment.polarity

    except Exception as e:
        print(e)

print(entityDict)

#TODO: algorithm for extracting multiword entites e.g "gift cards"

##use synnet to find similarity between words, find entity with most similarity score

##generate synsets for every enetity
synsetDict = {}

for entity in entityDict:

    nets = Word(entity).synsets
    if len(nets) > 0:
        net = nets[0]
        synsetDict[entity] = net

print(synsetDict)

##calculate entity with largest synset similarity score
synsetScoreDict = {}

for synsetEntity in synsetDict:

    synsetScoreDict[synsetEntity] = 0;

    for comparativeEntity in synsetDict:

        if(synsetEntity != comparativeEntity):

            entity1 = synsetDict[synsetEntity]
            entity2 = synsetDict[comparativeEntity]
            score = entity1.path_similarity(entity2)
            synsetScoreDict[synsetEntity] += score

print(synsetScoreDict)