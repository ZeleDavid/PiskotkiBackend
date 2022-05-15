import nltk
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import word_tokenize
from nltk import FreqDist
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
import string
from nltk.stem import PorterStemmer
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')

def getNames(names,name_father,name_mother):
    try:
        #df = pd.DataFrame({'name':names})
        df = pd.DataFrame(names, columns=['name'])
        #print(df.iloc[:, 0])

        #return ''
        #tokeni = word_tokenize(df.loc[['name']].values[0][0])
        tokeni = word_tokenize(df.iloc[:, 0].values[0])
        tokeni = [beseda.lower() for beseda in tokeni]

        #stop_list = stopwords.words('slovene') + list(string.punctuation)

        #tokeni_brez_stop = [token for token in tokeni if token not in stop_list]

        #tokeni_frekvenca_brez_stop = FreqDist(tokeni_brez_stop)

        stemmer = PorterStemmer()

        #tokeni_stemm = [stemmer.stem(beseda) for beseda in tokeni_brez_stop]
        tokeni_stemm = [stemmer.stem(beseda) for beseda in tokeni]

        tokeni_frekvenca_stem = FreqDist(tokeni_stemm)

        predlaganaImena = []
        for beseda, pogostost in tokeni_frekvenca_stem.most_common(10):
            print(f'{beseda:<15}: {pogostost}')
            predlaganaImena.append(beseda)

        return predlaganaImena
    except:
        return ""

def getSimilarNames(names,name_father,name_mother):
    try:
        #df = pd.DataFrame({'name':names})
        #print(df)
        if len(wn.synsets(name_father, lang='slv')):
            father = wn.synsets(name_father, lang='slv')[0]
        if len(wn.synsets(name_mother, lang='slv')):
            mother = wn.synsets(name_mother, lang='slv')[0]

        returnNames = []
        returnNameSimilarities = []
        for name in names:
            if len(wn.synsets(name, lang='slv')):
                nameset = wn.synsets(name, lang='slv')[0]
                if father and mother and nameset:
                    if father.path_similarity(nameset)>0.1:
                        returnNames.append(name)
                        returnNameSimilarities.append(father.path_similarity(nameset))
                    if mother.path_similarity(nameset)>0.1:
                        returnNames.append(name)
                        returnNameSimilarities.append(mother.path_similarity(nameset))

        max_value = max(returnNameSimilarities)
        max_index = returnNameSimilarities.index(max_value)
        return returnNames[max_index]
    except:
        return ""

    