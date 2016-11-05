from firebase import firebase
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.tokenize import WordPunctTokenizer
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from collections import defaultdict
from urllib import parse

#Define Globals

fireBaseUrl = "https://project-6747688871085580068.firebaseio.com"
sid = SentimentIntensityAnalyzer()
punctuation = ["?","!",",",".",";"]
questionKeywords = ["who", "what", "when", "why", "where", "whose", "whom", "which", "how"]



class Paragraph:
    def __init__(self, paragraph):
        self.paragraph = paragraph
        self.sentences = []

    def breakIntoSentences(self):
        sentenceToken = sent_tokenize(self.paragraph)

        wpt = WordPunctTokenizer()
        only_recognized_words = []

        for sentence in sentenceToken:
            tokens = wpt.tokenize(sentence)
            if tokens:
                for t in tokens:
                    if wordnet.synsets(t):
                        only_recognized_words.append(t)
            sentence = " ".join(only_recognized_words)
            self.sentences.append(Sentence(sentence))





#The sentence class, tracks everything regarding sentence structure and word types
class Sentence:

    #Initialize the sentence
    def __init__(self, sentence):
        #
        self.connoSentence = sid.polarity_scores(sentence)
        self.sentence = sentence.lower()
        self.connotation = (sid.polarity_scores(sentence)).get('compound')
        self.properNouns = []
        self.verbs = []
        self.pronouns = []
        self.adjectives = []
        self.adverbs = []
        self.wh_pronoun = []
        self.wh_adverb = []
        self.stop = set(stopwords.words('english'))
        self.words = []
        self.stopWords = []
        self.tokenSentence = word_tokenize(self.sentence)
        self.wordConno = defaultdict(list)
        self.sentenceType = "unknown"
        self.firebase = firebase.FirebaseApplication(fireBaseUrl, None)

    #Identify the words in the sentence, assign them to the appropriate arrays
    def identify(self):
        for word in nltk.pos_tag(self.tokenSentence):
            print(word)
            #is the word a stop word?
            if word[0] in self.stop:
                self.stopWords.append(word[0])
            #is the word a noun?
            if word[1] == "NNP" or word[1] == "NN":
                self.properNouns.append(word[0])
            #is the word a pronoun?
            if word[1] == "PRP":
                self.pronouns.append(word[0])
            #is the word a verb?
            if word[1] == "VB" or word[1] == "VBN" or word[1] == "VBG":
                self.verbs.append(word[0])
            #is the word an adjective?
            if word[1] == "JJ":
                self.adjectives.append(word[0])
            #is the word an adverb?
            if word[1] == "RB":
                self.adverbs.append(word[0])
            if word[1] == "WP":
                self.wh_pronoun.append(word[0])
            if word[1] == "WRB":
                self.wh_adverb.append(word[0])
            #i will add in more word types, so the AI will be able to better recognize the type of data is has received

    def breakIntoWords(self):
        #check individual word connotations to help the AI better understand the data
        for word in self.tokenSentence:
            if word not in punctuation:
                self.words.append(word)
                self.wordConno[word].append(sid.polarity_scores(word))

    def parseSentenceType(self):
        #check for the type of sentence
        #does it end with a question mark? then remove the question mark to stop it from causing issues when writing to the remote database.
        if self.sentence[-1:] == "?":
            self.sentenceType = "question"
            self.sentence = self.sentence[:-1]
        #does the sentence end with a ".", then remove the punctuation so it doesnt cause issues when writing to the remote database.
        elif self.sentence[-1:] == ".":
            self.sentenceType = "statement"
            self.sentence = self.sentence[:-1]
        # does the sentence end with a "!", then remove the punctuation so it doesnt cause issues when writing to the remote database.
        elif self.sentence[-1:] == "!":
            self.sentenceType = "exclamation"
            self.sentence = self.sentence[:-1]
        #does the sentence contain the 5 "w" words that normally make something a question? Used in case someone didnt use proper punctuation.
        elif self.sentence.partition(" ")[0] in questionKeywords:
            self.sentenceType = "question"
        #the sentence does not meet any of the required checks, set it to unknown
        else:
            self.sentenceType = "unknown"


    def submitSentence(self):
        self.parseSentenceType()
        # write the sentence to the remote database, so we can save it for later AI parsing
        sentenceResult = self.firebase.put(url='/sentences',
                                      data={'connotation': self.connotation, 'type': self.sentenceType},
                                      name=parse.quote_plus(self.sentence))
        self.identify()
        # console output
        print("Nouns: %s" % self.properNouns)
        print("Verbs: %s" % self.verbs)
        print("Pronouns: %s" % self.pronouns)
        print(self.connotation)

        self.breakIntoWords()

        # check if word is in any of the arrays, then post that to the remote database for later AI parsing
        for word in self.wordConno:
            if word in self.properNouns:
                wordType = "noun"
            elif word in self.verbs:
                wordType = "verb"
            elif word in self.pronouns:
                wordType = "pronoun"
            elif word in self.adverbs:
                wordType = "adverb"
            elif word in self.adjectives:
                wordType = "adjective"
            elif word in self.wh_adverb:
                wordType = "wh_adverb"
            elif word in self.wh_pronoun:
                wordType = "wh_pronoun"
            else:
                wordType = "unknown"
            # console output
            print("-", word)
            print("     neutral:  ", self.wordConno.get(word)[0].get('neu'))
            print("     negative: ", self.wordConno.get(word)[0].get('neg'))
            print("     positive: ", self.wordConno.get(word)[0].get('pos'))
            # write the word, wordtype, and connotations to the remote database
            wordResult = self.firebase.put(url='/words', name=word,
                                      data={'type': wordType, 'neutral': self.wordConno.get(word)[0].get('neu'),
                                            'negative': self.wordConno.get(word)[0].get('neg'),
                                            'positive': self.wordConno.get(word)[0].get('pos')})