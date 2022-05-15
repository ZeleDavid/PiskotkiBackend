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
        name = request.json.get('name')
        action = request.json.get('action')
    except:
        return {'message': 'Missing some arguments'}, 400

    if name is None or action is None:
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
    return {'message': 'Not implemented'}, 400

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

    decoded = jwt.decode(get_token(request.headers['authorization']), options={"verify_signature": False})
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
    
    name = getSimilarNames(list(names),name_father,name_mother)
    if name == "":
        name = getNames(list(names),name_father,name_mother)

    return {'name': name}