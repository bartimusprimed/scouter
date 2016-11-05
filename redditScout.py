from scouter import Sentence
from scouter import Paragraph
import praw
import re
from string import whitespace



config = {}
with open("/Users/samuelbarthelemy/redditCred") as f:
    for line in f:
        line = line.rstrip("\n")
        (key, val) = line.split("=")
        config[key] = val



def searchReddit(search, after=None):
    r = praw.Reddit(user_agent='Mozilla Firefox')
    r.login(config['username'], config['password'], disable_warning=True)
    posts = r.search(search, subreddit=None, sort=None, syntax=None, period=None, limit=50)
    for post in posts:
        post = post.title
        post = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", post).split())
        post = re.sub('RT', '', post)
        post = re.sub('https', '', post)
        post = re.sub('[^a-zA-Z0-9 \n\.]', '', post)
        post = re.sub('Megathread', '', post)
        post = post.lstrip(whitespace)
        post = Sentence(post)
        post.submitSentence()

searchReddit("hillary clinton")






