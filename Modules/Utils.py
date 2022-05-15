#import pandas as pd

USER_ID = dict()

def setUserID(token, user_id):
    global USER_ID
    USER_ID[token] = user_id

def getUserID(token):
    return USER_ID[token]

def getData():
    #TO DO: preberemo imena iz baze ali datoteke
    #data = pd.read_csv("./Data/allData.csv")
    data = 'IME placeholder'
    print(data)
    return data