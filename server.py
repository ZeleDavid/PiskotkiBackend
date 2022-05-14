from flask import Flask, request, jsonify
import Modules.Utils as Utils
import Modules.UserManagement as UserManagement
import random
from firebase_admin import firestore

USER_ID = "ASnc71OP5BhmP7c5dTOfthLLzo42"

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/getNextName')
def returnNextName():
    with app.app_context():
        managedData = Utils.getData()
        #TO DO: algoritem, ki ti vrne najprimernejše ime
        
    return "Izpis naslednjega imena"

@app.route('/getRandomName')
def returnRandomName():
    with app.app_context():
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
    
    
@app.route('/userinfo')
def userinfo():
    with app.app_context():
        return UserManagement.userinfo()
    return "User info"

@app.route('/settings', methods = ['GET'])
def getsettings():
    with app.app_context():
        return UserManagement.getsettings()
    return "Settings"

@app.route('/settings', methods = ['POST'])
def settings():
    with app.app_context():
        return UserManagement.setsettings(request)
    return "Settings"

@app.route('/signup',methods = ['POST', 'GET'])
def signup():
    with app.app_context():
        return UserManagement.signup(request)
    return "Sign up"

@app.route('/token',methods = ['POST', 'GET'])
def token():
    with app.app_context():
        return UserManagement.token(request)
    return "Token"

@app.route('/signout')
def signout():
    with app.app_context():
        return UserManagement.signout()
    return "Sign out"

if __name__ == '__main__':
    app.run(debug=True, port=0)