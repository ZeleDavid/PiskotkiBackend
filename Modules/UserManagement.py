#Imports
import firebase_admin
import pyrebase
import json
from firebase_admin import credentials, auth, firestore
from flask import Flask, request
from functools import wraps

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
#Data source
users = [{'uid': 1, 'name': 'Noah Schairer'}]

@check_token
def userinfo():
    return {'data': users}, 200

@check_token
def getsettings():
    db = firestore.client()
    doc_ref = db.collection(u'settings').document(USER_ID)
    doc = doc_ref.get()
    
    if doc.exists:
        print(doc.to_dict())
    else:
        return {'message': 'No settings found'}, 400

    return doc.to_dict(), 200

@check_token
def setsettings(request):
    try:
        first_character = request.form.get('first_character')
        length_min = request.form.get('length_min')
        length_max = request.form.get('length_max')
        gender = request.form.get('gender')

        print(first_character)
        print(length_min)
        print(length_max)
        print(gender)

        if first_character is None or length_min is None or length_max is None or gender is None:
            return {'message': 'Missing some arguments'}, 400

        data = {
            u'first_character': first_character,
            u'length_min': length_min,
            u'length_max': length_max,
            u'gender': gender
        }

        db = firestore.client()

        doc_ref = db.collection(u'settings').document(USER_ID)
        doc_ref.set(data)

        return {'message': 'succesfully saved user settings'}, 200
    except:
        return {'message': 'Error saving user settings'}, 400

    
def signup(request):
    email = request.body.get('email')
    password = request.body.get('password')
    if email is None or password is None:
        return {'message': 'Error missing email or password'},400
    try:
        user = auth.create_user(
               email=email,
               password=password
        )
        return {'message': f'Successfully created user {user.uid}'},200
    except:
        return {'message': 'Error creating user'},400
        
def token(request):
    email = request.body.get('email')
    password = request.body.get('password')
    try:
        user = pb.auth().sign_in_with_email_and_password(email, password)
        jwt = user['idToken']
        return {'token': jwt}, 200
    except:
        return {'message': 'There was an error logging in'},400

def signout():
    pb.auth().current_user = None
    return {'message': f'Successfully signed user out.'},200