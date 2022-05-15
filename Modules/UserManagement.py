#Imports
import firebase_admin
import pyrebase
import json
from firebase_admin import credentials, auth, firestore
from flask import Flask, request
from functools import wraps

from Modules.Utils import getUserID, setUserID
import jwt

PREFIX = 'Bearer '

def get_token(header):
    if not header.startswith(PREFIX):
        raise ValueError('Invalid token')

    return header[len(PREFIX):]

def check_token(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if not request.headers.get('authorization'):
            return {'message': 'No token provided'},400
        try:
            user = auth.verify_id_token(get_token(request.headers['authorization']))
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
    #doc_ref = db.collection(u'settings').document(getUserID(get_token(request.headers['authorization'])))
    decoded = jwt.decode(get_token(request.headers['authorization']), options={"verify_signature": False})
    doc_ref = db.collection(u'settings').document(decoded.user_id)
    doc = doc_ref.get()

    if doc.exists:
        print(doc.to_dict())
    else:
        return {'message': 'No settings found'}, 400

    return doc.to_dict(), 200

@check_token
def setsettings():
    try:
        first_character = request.json.get('first_character')
        last_character = request.json.get('last_character')

        length_short = request.json.get('length_short')
        length_medium = request.json.get('length_medium')
        length_long = request.json.get('length_long')

        style_modern = request.json.get('style_modern')
        style_classic = request.json.get('style_classic')

        name_father = request.json.get('name_father')
        name_mother = request.json.get('name_mother')

        sibling_names = request.json.get('sibling_names')

        gender = request.json.get('gender')

        if first_character is None or last_character is None or length_short is None or length_medium is None or length_long is None or style_classic is None or style_modern is None or name_father is None or name_mother is None or gender is None:
            return {'message': 'Missing some arguments'}, 400

        data = {
            u'first_character': first_character,
            u'last_character': last_character,
            u'length_short': length_short,
            u'length_medium': length_medium,
            u'length_long': length_long,
            u'style_modern': style_modern,
            u'style_classic': style_classic,
            u'name_father': name_father,
            u'name_mother': name_mother,
            u'gender': gender
        }

        db = firestore.client()

        doc_ref = db.collection(u'settings').document(getUserID(get_token(request.headers['authorization'])))
        doc_ref.set(data)

        return {'message': 'succesfully saved user settings'}, 200
    except:
        return {'message': 'Error saving user settings'}, 400

def signup():
    email = request.json.get('email')
    password = request.json.get('password')
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
        
def signin():
    email = request.json.get('email')
    password = request.json.get('password')
    try:
        user = pb.auth().sign_in_with_email_and_password(email, password)
        jwt = user['idToken']
        setUserID(jwt, user['localId'])
        return {'token': jwt}, 200
    except:
        return {'message': 'There was an error logging in'},400

@check_token
def signout():
    pb.auth().current_user = None
    return {'message': f'Successfully signed user out.'},200