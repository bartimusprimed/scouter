import twitter
import re
from string import whitespace
from scouter import Sentence
from scouter import Paragraph

from urllib import parse

config = {}
with open("/Users/samuelbarthelemy/config.py") as f:
    for line in f:
        line = line.rstrip("\n")
        (key, val) = line.split("=")
        config[key] = val
print(config)
api = twitter.Api(access_token_key=config["access_key"], access_token_secret=config["access_secret"], consumer_key=config["consumer_key"], consumer_secret=config["consumer_secret"])


query = api.GetSearch(term="donald trump", count=100, result_type="recent")
for result in query:
    tweet = result.AsDict()["text"]
    tweet = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
    tweet = re.sub('RT', '', tweet)
    tweet = re.sub('https', '', tweet)
    tweet = re.sub('[^a-zA-Z0-9 \n\.]', '', tweet)
    tweet = tweet.lstrip(whitespace)
    if len(tweet) <= 0:
        break
    tweet = Paragraph(tweet)
    tweet.breakIntoSentences()
    for sentence in tweet.sentences:
        sentence.submitSentence()