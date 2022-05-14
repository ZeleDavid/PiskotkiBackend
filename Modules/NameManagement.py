#Imports
import firebase_admin
import pyrebase
import json
from firebase_admin import credentials, auth, firestore
from flask import Flask, request
from functools import wraps
import random

USER_ID = u'ASnc71OP5BhmP7c5dTOfthLLzo42'

def check_token(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if not request.headers.get('authorization'):
            return {'message': 'No token provided'},400
        try:
            user = auth.verify_id_token(request.headers['authorization'])
            request.user = user
        except:
            return {'message':'Invalid token provided.'},400
        return f(*args, **kwargs)
    return wrap

#Connect to firebase
cred = credentials.Certificate('fbAdminConfig.json')
firebase = firebase_admin.initialize_app(cred)
pb = pyrebase.initialize_app(json.load(open('fbconfig.json')))


@check_token
def getrandomname():
    db = firestore.client()

    used_names = set()
    actions = db.collection(u'action').where(u'user_ID', u'==', USER_ID).stream()
    for doc in actions:
        used_names.add(doc.to_dict()['name_ID'])

    names_stream = db.collection(u'name').stream()

    names = set()

    for doc in names_stream:
        if(len(names) > 100): break
        if doc.id not in used_names:
            names.add(doc.to_dict()['name'])
    
    return random.sample(names, 1)[0]


@check_token
def postNameAction(request):
    try:
        name = request.form.get('name')
        action = request.form.get('action')
    except:
        return {'message': 'Missing some arguments'}, 400

    if name is None or action is None:
        return {'message': 'Missing some arguments'}, 400
    try:
        db = firestore.client()
        doc_ref = db.collection(u'action').document()
        doc_ref.set({
            u'user_ID': USER_ID,
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

    actions = db.collection(u'action').where(u'user_ID', u'==', USER_ID).stream()

    return_actions = []

    for doc in actions:
        return_actions.append(doc.to_dict())

    return {'data': return_actions}, 200


@check_token
def deleteNameAction(request):
    try:
        name = request.form.get('name')
        action = request.form.get('action')
    except:
        return {'message': 'Missing some arguments'}, 400

    if name is None or action is None:
        return {'message': 'Missing some arguments'}, 400
    try:
        db = firestore.client()
        doc_ref = db.collection(u'action').where(u'user_ID', u'==', USER_ID).where(u'name_ID', u'==', name).stream()
        for doc in doc_ref:
            doc.reference.delete()
        return {'message': 'Success'}, 200
    except:
        return {'message': 'Something went wrong'}, 400

@check_token
def purgeNameActions():
    db = firestore.client()

    actions = db.collection(u'action').where(u'user_ID', u'==', USER_ID).stream()

    for doc in actions:
        doc.reference.delete()

    return {'message': 'Success'}, 200