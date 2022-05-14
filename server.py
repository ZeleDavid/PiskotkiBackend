from flask import Flask, request, jsonify
import Modules.Utils as Utils
import Modules.UserManagement as UserManagement
import Modules.NameManagement as NameManagement
import random
from firebase_admin import firestore
from flask_cors import CORS, cross_origin

USER_ID = None

def setUserID(user_id):
    USER_ID = user_id

def getUserID():
    return USER_ID

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

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
        return NameManagement.getrandomname()
    return "Random name"

@app.route('/suggestNameBasedOnOthers')
def suggestNameBasedOnOthers():
    with app.app_context():
        return NameManagement.suggestNameBasedOnOthers()
    return "Suggested name"

@app.route('/nameAction', methods=['POST'])
def postNameAction(request):
    with app.app_context():
        return NameManagement.postNameAction(request)
    return "Name action"

@app.route('/nameAction', methods=['GET'])
def getNameAction(request):
    with app.app_context():
        return NameManagement.getNameActions(request)
    return "Name action"

@app.route('/nameAction' , methods=['DELETE'])
def deleteNameAction(request):
    with app.app_context():
        return NameManagement.deleteNameAction(request)
    return "Name action"

@app.route('/nameAction', methods=['PURGE'])
def purgeNameAction(request):
    with app.app_context():
        return NameManagement.purgeNameActions(request)
    return "Name action"

@app.route('/')
    
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

@app.route('/signup',methods = ['POST'])
def signup():
    with app.app_context():
        return UserManagement.signup(request)
    return "Sign up"

@app.route('/signin',methods = ['POST'])
def signin():
    with app.app_context():
        return UserManagement.signin(request)
    return "Sign in"

@app.route('/signout')
def signout():
    with app.app_context():
        return UserManagement.signout()
    return "Sign out"

if __name__ == '__main__':
    app.run(debug=True, port=0)