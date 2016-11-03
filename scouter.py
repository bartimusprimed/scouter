from firebase import firebase
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict

#Define Globals

fireBaseUrl = "https://project-6747688871085580068.firebaseio.com"
sid = SentimentIntensityAnalyzer()
punctuation = ["?","!",",",".",";"]
questionKeywords = ["who", "what", "when", "why", "where", "whose", "whom", "which", "how"]




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
            if word[1] == "VB" or word[1] == "VBN":
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
        if sentence.sentence[-1:] == "?":
            sentence.sentenceType = "question"
            sentence.sentence = sentence.sentence[:-1]
        #does the sentence end with a ".", then remove the punctuation so it doesnt cause issues when writing to the remote database.
        elif sentence.sentence[-1:] == ".":
            sentence.sentenceType = "statement"
            sentence.sentence = sentence.sentence[:-1]
        # does the sentence end with a "!", then remove the punctuation so it doesnt cause issues when writing to the remote database.
        elif sentence.sentence[-1:] == "!":
            sentence.sentenceType = "exclamation"
            sentence.sentence = sentence.sentence[:-1]
        #does the sentence contain the 5 "w" words that normally make something a question? Used in case someone didnt use proper punctuation.
        elif sentence.sentence.partition(" ")[0] in questionKeywords:
            sentence.sentenceType = "question"
        #the sentence does not meet any of the required checks, set it to unknown
        else:
            sentence.sentenceType = "unknown"


sentences = [Sentence("What is the time"), Sentence("Who are you?"), Sentence("i hate being outside."), Sentence("here is another sentence"), Sentence("Shut Up!")]

#define the firebase database need to make this read from a file so all of github doesn't have access to write to the database
firebase = firebase.FirebaseApplication(fireBaseUrl, None)

for sentence in sentences:
    sentence.parseSentenceType()
    #write the sentence to the remote database, so we can save it for later AI parsing
    sentenceResult = firebase.put(url='/sentences', data={'connotation': sentence.connotation, 'type': sentence.sentenceType}, name=sentence.sentence)
    sentence.identify()
    #console output
    print("Nouns: %s" % sentence.properNouns)
    print("Verbs: %s" % sentence.verbs)
    print("Pronouns: %s" % sentence.pronouns)
    print(sentence.connotation)

    sentence.breakIntoWords()

    #check if word is in any of the arrays, then post that to the remote database for later AI parsing
    for word in sentence.wordConno:
        if word in sentence.properNouns:
            wordType = "noun"
        elif word in sentence.verbs:
            wordType = "verb"
        elif word in sentence.pronouns:
            wordType = "pronoun"
        elif word in sentence.adverbs:
            wordType = "adverb"
        elif word in sentence.adjectives:
            wordType = "adjective"
        elif word in sentence.wh_adverb:
            wordType = "wh_adverb"
        elif word in sentence.wh_pronoun:
            wordType = "wh_pronoun"
        else:
            wordType = "unknown"
        #console output
        print("-", word)
        print("     neutral:  ", sentence.wordConno.get(word)[0].get('neu'))
        print("     negative: ", sentence.wordConno.get(word)[0].get('neg'))
        print("     positive: ", sentence.wordConno.get(word)[0].get('pos'))
        #write the word, wordtype, and connotations to the remote database
        wordResult = firebase.put(url='/words', name=word, data={'type': wordType, 'neutral': sentence.wordConno.get(word)[0].get('neu'), 'negative': sentence.wordConno.get(word)[0].get('neg'), 'positive': sentence.wordConno.get(word)[0].get('pos')})