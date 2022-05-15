#Imports
import firebase_admin
import pyrebase
import json
from firebase_admin import credentials, auth, firestore
from flask import Flask, request
from functools import wraps
import random
from Modules.UserManagement import check_token, get_token
from Modules.NameProcessing import getSimilarNames
from Modules.NameProcessing import getNames
import jwt
import math

pb = pyrebase.initialize_app(json.load(open('fbconfig.json')))


@check_token
def getrandomname():
    db = firestore.client()

    used_names = set()
    print(get_token(request.headers['authorization']))
    decoded = jwt.decode(get_token(request.headers['authorization']), options={"verify_signature": False})

    actions = db.collection(u'action').where(u'user_ID', u'==', decoded["user_id"]).stream()
    for doc in actions:
        used_names.add(doc.to_dict()['name_ID'])

    names_stream = db.collection(u'name').stream()

    names = set()
    name_key = dict()

    gender = db.collection(u'settings').document(decoded["user_id"]).get().to_dict()["gender"]

    for doc in names_stream:
        if(len(names) > 100): break
        if doc.id not in used_names and doc.to_dict()['gender'] == gender:
            names.add(doc.to_dict()['name'])
            name_key[doc.to_dict()['name']] = doc.id
    
    if len(names) == 0:
        return {'message': 'No names left'}, 400

    name = random.choice(list(names))
    return {'name_ID': name_key[name] , 'name': name}


@check_token
def postNameAction():
    try:
        name = request.json.get('name')
        action = request.json.get('action')
    except:
        return {'message': 'Missing some arguments'}, 400

    if name is None or action is None:
        return {'message': 'Missing some arguments'}, 400
    try:
        db = firestore.client()
        doc_ref = db.collection(u'action').document()
        decoded = jwt.decode(get_token(request.headers['authorization']), options={"verify_signature": False})
        doc_ref.set({
            u'user_ID': decoded["user_id"],
            u'name_ID': name,
            u'action': action,
        })
        return {'message': 'Success'}, 200
    except:
        return {'message': 'Something went wrong'}, 400


@check_token
def getNameActions():
    db = firestore.client()

    decoded = jwt.decode(get_token(request.headers['authorization']), options={"verify_signature": False})
    actions = db.collection(u'action').where(u'user_ID', u'==', decoded["user_id"]).stream()

    return_actions = []

    for doc in actions:
        temp_dict = doc.to_dict()
        temp_dict['name'] = db.collection('name').document(temp_dict['name_ID']).get().to_dict()['name']
        return_actions.append(temp_dict)

    return {'data': return_actions}, 200


@check_token
def deleteNameAction():
    try:
        name = request.args.get('name');
    except:
        return {'message': 'Missing some arguments'}, 400

    if name is None:
        return {'message': 'Missing some arguments'}, 400
    try:
        db = firestore.client()
        decoded = jwt.decode(get_token(request.headers['authorization']), options={"verify_signature": False})
        doc_ref = db.collection(u'action').where(u'user_ID', u'==', decoded["user_id"]).where(u'name_ID', u'==', name).stream()
        for doc in doc_ref:
            doc.reference.delete()
        return {'message': 'Success'}, 200
    except:
        return {'message': 'Something went wrong'}, 400

@check_token
def purgeNameActions():
    db = firestore.client()

    decoded = jwt.decode(get_token(request.headers['authorization']), options={"verify_signature": False})
    actions = db.collection(u'action').where(u'user_ID', u'==', decoded["user_id"]).stream()

    for doc in actions:
        doc.reference.delete()

    return {'message': 'Success'}, 200

@check_token
def getStatistics():
    try:
        year = request.json.get('year')
    except:
        return {'message': 'Missing some arguments'}, 400

    db = firestore.client()
    
    men = []
    women = []

    stream = db.collection('name_all').where(u'year', u'==', year).stream()

    for doc in stream:
        if not math.isnan(doc['count']):
            if doc['gender']:
                men.append([doc['name_ID'], doc['count']])
            else:
                women.append([doc['name_ID'], doc['count']])

    men = reversed(men.sort(key = lambda x: x[1]))
    women = reversed(women.sort(key = lambda x: x[1]))


    return {'men': men, 'women': women}, 200

@check_token
def suggestNameBasedOnOthers():
    db = firestore.client()

    used_names = set()
    decoded = jwt.decode(get_token(request.headers['authorization']), options={"verify_signature": False})
    actions = db.collection(u'action').where(u'user_ID', u'==', decoded["user_id"]).stream()
    for doc in actions:
        used_names.add(doc.to_dict()['name_ID'])

    names_stream = db.collection(u'name').stream()

    names = set()

    doc_ref = db.collection(u'settings').document(decoded["user_id"])
    docr = doc_ref.get()
    if docr.exists:
        docrr = docr.to_dict()
        name_father = docrr['name_father']
        name_mother = docrr['name_mother']
    
    for doc in names_stream:
        if(len(names) > 100): break
        if doc.id not in used_names:
            names.add(doc.to_dict()['name'])
    
    chance = random.randint(1,100)
    name = ""
    if (chance <=50) and docr.exists:
        name = getSimilarNames(list(names),name_father,name_mother)
    if name == "":
        name = getPreferencesBasedOnHistory(decoded)
        if name == "" and len(getNames(list(names))[0])>0:
            name = getNames(list(names))[0]
        #if not chosen by algorithm, choose randomly
        else:
            used_names = set()
            actions = db.collection(u'action').where(u'user_ID', u'==', decoded["user_id"]).stream()
            for doc in actions:
                used_names.add(doc.to_dict()['name_ID'])

            names_stream = db.collection(u'name').stream()

            names = set()
            name_key = dict()

            for doc in names_stream:
                if(len(names) > 100): break
                if doc.id not in used_names:
                    names.add(doc.to_dict()['name'])
                    name_key[doc.to_dict()['name']] = doc.id
            
            if len(names) == 0:
                return {'message': 'No names left'}, 400

            name = random.choice(list(names))
            return {'name_ID': name_key[name] , 'name': name}

    return {'name': name}

def getPreferencesBasedOnHistory(decoded):
    db = firestore.client()

    #Liked kid
    actions = db.collection(u'action').where(u'user_ID', u'==', decoded["user_id"]).where(u'action', u'==', "like").stream()

    temp_dict = []
    for doc in actions:
        temp_dict = doc.to_dict()
        temp_dict['name'] = db.collection('name').document(temp_dict['name_ID']).where(u'kid', u'==', True).get().to_dict()['name']
    
    likedKid = len(temp_dict)

    #Disliked kid
    actions = db.collection(u'action').where(u'user_ID', u'==', decoded["user_id"]).where(u'action', u'==', "dislike").stream()

    for doc in actions:
        temp_dict = doc.to_dict()
        temp_dict['name'] = db.collection('name').document(temp_dict['name_ID']).where(u'kid', u'==', True).get().to_dict()['name']
    
    dislikedKid = len(temp_dict)

    #Superliked kid
    actions = db.collection(u'action').where(u'user_ID', u'==', decoded["user_id"]).where(u'action', u'==', "superlike").stream()

    for doc in actions:
        temp_dict = doc.to_dict()
        temp_dict['name'] = db.collection('name').document(temp_dict['name_ID']).where(u'kid', u'==', True).get().to_dict()['name']
    
    superlikedKid = len(temp_dict)

    #Liked adult
    actions = db.collection(u'action').where(u'user_ID', u'==', decoded["user_id"]).where(u'action', u'==', "like").stream()

    for doc in actions:
        temp_dict = doc.to_dict()
        temp_dict['name'] = db.collection('name').document(temp_dict['name_ID']).where(u'kid', u'==', False).get().to_dict()['name']
    
    likedAdult = len(temp_dict)

    #Disliked adult
    actions = db.collection(u'action').where(u'user_ID', u'==', decoded["user_id"]).where(u'action', u'==', "dislike").stream()

    for doc in actions:
        temp_dict = doc.to_dict()
        temp_dict['name'] = db.collection('name').document(temp_dict['name_ID']).where(u'kid', u'==', False).get().to_dict()['name']
    
    dislikedAdult = len(temp_dict)

    #Superliked adult
    actions = db.collection(u'action').where(u'user_ID', u'==', decoded["user_id"]).where(u'action', u'==', "superlike").stream()

    for doc in actions:
        temp_dict = doc.to_dict()
        temp_dict['name'] = db.collection('name').document(temp_dict['name_ID']).where(u'kid', u'==', False).get().to_dict()['name']
    
    superlikedAdult = len(temp_dict)

    if 2*superlikedKid + likedKid > dislikedKid:
        kid = True
    else:
        kid = False

    if 2*superlikedAdult + likedAdult > dislikedAdult:
        adult = True
    else:
        adult = False

    gender = db.collection(u'settings').document(decoded["user_id"]).get().to_dict()['gender']
    first_character = db.collection(u'settings').document(decoded["user_id"]).get().to_dict()['first_character']
    last_character = db.collection(u'settings').document(decoded["user_id"]).get().to_dict()['last_character']
    length_long = db.collection(u'settings').document(decoded["user_id"]).get().to_dict()['length_long']
    length_medium = db.collection(u'settings').document(decoded["user_id"]).get().to_dict()['length_medium']
    #length_short = db.collection(u'settings').document(decoded["user_id"]).get().to_dict()['length_short']
    length_short = True
    style_classic = db.collection(u'settings').document(decoded["user_id"]).get().to_dict()['style_classic']
    style_modern = db.collection(u'settings').document(decoded["user_id"]).get().to_dict()['style_modern']
    used_names = set()
    
    chance = random.randint(1,100)
    if chance <=80:
        if adult:
            actions = db.collection(u'action').where(u'user_ID', u'==', decoded["user_id"]).where(u'kid', u'==', kid).stream()
        else:
            actions = db.collection(u'action').where(u'user_ID', u'==', decoded["user_id"]).where(u'kid', u'==', kid).stream()
    else:
        actions = db.collection(u'action').where(u'user_ID', u'==', decoded["user_id"]).stream()
    for doc in actions:
        used_names.add(doc.to_dict()['name_ID'])

    names_stream = db.collection(u'name').stream()

    names = set()
    name_key = dict()

    for doc in names_stream:
        if(len(names) > 100): break
        if doc.id not in used_names and doc.to_dict()['gender'] == gender:
            if first_character != "":
                if(doc.to_dict()['name'].startswith(first_character) == False):
                    continue 
            if last_character != "":
                if(doc.to_dict()['name'].endswith(last_character) == False):
                    continue
            if length_short == False:
                if(len(doc.to_dict()['name']) < 5):
                    continue  
            if length_medium == False:
                if(len(doc.to_dict()['name']) < 7 and len(doc.to_dict()['name']) > 4):
                    continue
            if length_long == False:
                if(len(doc.to_dict()['name']) > 6):
                    continue
            if style_classic == False:
                if doc.to_dict()['kid'] == False:
                    continue
            if style_modern == False:
                if doc.to_dict()['kid'] == True:
                    continue
            names.add(doc.to_dict()['name'])
            name_key[doc.to_dict()['name']] = doc.id

    if(len(list(names))>0):
        name = random.choice(list(names))
        return {'name_ID': name_key[name] , 'name': name}
    else: return ""