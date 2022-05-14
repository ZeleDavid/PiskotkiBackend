import nltk
import pandas as pd

from nltk.tokenize import word_tokenize
from nltk import FreqDist
from nltk.corpus import stopwords
import string
from nltk.stem import PorterStemmer

tokeni = word_tokenize(df.loc[['Slovenia'],['background']].values[0][0])
tokeni = [beseda.lower() for beseda in tokeni]

#stop_list = stopwords.words('english') + list(string.punctuation)

#tokeni_brez_stop = [token for token in tokeni if token not in stop_list]

#tokeni_frekvenca_brez_stop = FreqDist(tokeni_brez_stop)
tokeni_frekvenca_brez_stop = FreqDist(tokeni)

stemmer = PorterStemmer()

#tokeni_stemm = [stemmer.stem(beseda) for beseda in tokeni_brez_stop]
tokeni_stemm = [stemmer.stem(beseda) for beseda in tokeni]

tokeni_frekvenca_stem = FreqDist(tokeni_stemm)
for beseda, pogostost in tokeni_frekvenca_stem.most_common(10):
  print(f'{beseda:<15}: {pogostost}')