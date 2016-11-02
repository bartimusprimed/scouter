from firebase import firebase
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict

fireBaseUrl = "https://project-6747688871085580068.firebaseio.com"
sid = SentimentIntensityAnalyzer()
punctuation = ["?","!",",",".",";"]
questionKeywords = ["who", "what", "when", "why", "where"]


class Sentence:


    def __init__(self, sentence):
        self.connoSentence = sid.polarity_scores(sentence)
        self.sentence = sentence.lower()
        self.connotation = (sid.polarity_scores(sentence)).get('compound')
        self.properNouns = []
        self.verbs = []
        self.stop = set(stopwords.words('english'))
        self.words = []
        self.tokenSentence = word_tokenize(self.sentence)
        self.wordConno = defaultdict(list)
        self.sentenceType = "unknown"
    def identify(self):
        for word in nltk.pos_tag(self.tokenSentence):
            print(word)
            #if word[0] not in self.stop:
            if word[1] == "NNP" or word[1] == "NN" or word[1] == "PRP":
                self.properNouns.append(word[0])
            if word[1] == "VB" or word[1] == "VBN":
                self.verbs.append(word[0])

    def breakIntoWords(self):
        for word in self.tokenSentence:
            if word not in punctuation:
                self.words.append(word)
                self.wordConno[word].append(sid.polarity_scores(word))

    def parseSentenceType(self):
        if sentence.sentence[-1:] == "?":
            sentence.sentenceType = "question"
            sentence.sentence = sentence.sentence[:-1]
        elif sentence.sentence.partition(" ")[0].lower() in questionKeywords:
            sentence.sentenceType = "question"
        elif sentence.sentence[-1:] == ".":
            sentence.sentenceType = "statement"
            sentence.sentence = sentence.sentence[:-1]
        elif sentence.sentence[-1:] == "!":
            sentence.sentenceType = "exclamation"
            sentence.sentence = sentence.sentence[:-1]
        else:
            sentence.sentenceType = "unknown"


sentences = [Sentence("What is the time"), Sentence("Who are you?"), Sentence("i hate being outside."), Sentence("here is another sentence"), Sentence("Shut Up!")]


firebase = firebase.FirebaseApplication(fireBaseUrl, None)

for sentence in sentences:
    sentence.parseSentenceType()
    sentenceResult = firebase.put(url='/sentences', data={'connotation': sentence.connotation, 'type': sentence.sentenceType}, name=sentence.sentence)
    sentence.identify()
    print("Nouns: %s" % sentence.properNouns)
    print("Verbs: %s" % sentence.verbs)
    print(sentence.connotation)
    sentence.breakIntoWords()
    print(sentence.words)
    for word in sentence.wordConno:
        if word in sentence.properNouns:
            wordType = "noun"
        elif word in sentence.verbs:
            wordType = "verb"
        else:
            wordType = "unknown"
        print("-", word)
        print("     neutral:  ", sentence.wordConno.get(word)[0].get('neu'))
        print("     negative: ", sentence.wordConno.get(word)[0].get('neg'))
        print("     positive: ", sentence.wordConno.get(word)[0].get('pos'))
        wordResult = firebase.put(url='/words', name=word, data={'type': wordType, 'neutral': sentence.wordConno.get(word)[0].get('neu'), 'negative': sentence.wordConno.get(word)[0].get('neg'), 'positive': sentence.wordConno.get(word)[0].get('pos')})