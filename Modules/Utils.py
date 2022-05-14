#import pandas as pd

USER_ID = None

def setUserID(user_id):
    USER_ID = user_id

def getUserID():
    return USER_ID

def getData():
    #TO DO: preberemo imena iz baze ali datoteke
    #data = pd.read_csv("./Data/allData.csv")
    data = 'IME placeholder'
    print(data)
    return data