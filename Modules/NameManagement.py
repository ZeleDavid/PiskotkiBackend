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

from Modules.Utils import getUserID

pb = pyrebase.initialize_app(json.load(open('fbconfig.json')))


@check_token
def getrandomname():
    db = firestore.client()

    used_names = set()
    actions = db.collection(u'action').where(u'user_ID', u'==', getUserID(get_token(request.headers['authorization']))).stream()
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
        doc_ref.set({
            u'user_ID': getUserID(get_token(request.headers['authorization'])),
            u'name_ID': name,
            u'action': action,
            u'timestamp': firestore.SERVER_TIMESTAMP
        })
        return {'message': 'Success'}, 200
    except:
        return {'message': 'Something went wrong'}, 400


@check_token
def getNameActions():
    db = firestore.client()

    actions = db.collection(u'action').where(u'user_ID', u'==', getUserID(get_token(request.headers['authorization']))).stream()

    return_actions = []

    for doc in actions:
        temp_dict = doc.to_dict()
        temp_dict['name'] = db.collection('name').document(temp_dict['name_ID']).get().to_dict()['name']
        return_actions.append(doc.to_dict())

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
        doc_ref = db.collection(u'action').where(u'user_ID', u'==', getUserID(get_token(request.headers['authorization']))).where(u'name_ID', u'==', name).stream()
        for doc in doc_ref:
            doc.reference.delete()
        return {'message': 'Success'}, 200
    except:
        return {'message': 'Something went wrong'}, 400

@check_token
def purgeNameActions():
    db = firestore.client()

    actions = db.collection(u'action').where(u'user_ID', u'==', getUserID(get_token(request.headers['authorization']))).stream()

    for doc in actions:
        doc.reference.delete()

    return {'message': 'Success'}, 200

@check_token
def suggestNameBasedOnOthers():
    db = firestore.client()

    used_names = set()
    actions = db.collection(u'action').where(u'user_ID', u'==', getUserID(get_token(request.headers['authorization']))).stream()
    for doc in actions:
        used_names.add(doc.to_dict()['name_ID'])

    names_stream = db.collection(u'name').stream()

    names = set()

    doc_ref = db.collection(u'settings').document(getUserID(get_token(request.headers['authorization'])))
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

    return {'name': name}