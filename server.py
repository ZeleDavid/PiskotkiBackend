from flask import Flask, request, jsonify
import Modules.Utils as Utils
import Modules.UserManagement as UserManagement
import Modules.NameManagement as NameManagement
import random
from firebase_admin import firestore
from flask_cors import CORS, cross_origin

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

@app.route('/getSuggestedName')
def suggestNameBasedOnOthers():
    with app.app_context():
        return NameManagement.suggestNameBasedOnOthers()
    return "Suggested name"

@app.route('/nameAction', methods=['POST'])
def postNameAction():
    with app.app_context():
        return NameManagement.postNameAction()
    return "Name action"

@app.route('/nameAction', methods=['GET'])
def getNameAction():
    with app.app_context():
        return NameManagement.getNameActions()
    return "Name action"

@app.route('/nameAction' , methods=['DELETE'])
def deleteNameAction():
    with app.app_context():
        return NameManagement.deleteNameAction()
    return "Name action"

@app.route('/nameAction', methods=['PURGE'])
def purgeNameAction():
    with app.app_context():
        return NameManagement.purgeNameActions()
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
        return UserManagement.setsettings()
    return "Settings"

@app.route('/signup',methods = ['POST'])
def signup():
    with app.app_context():
        return UserManagement.signup()
    return "Sign up"

@app.route('/signin',methods = ['POST'])
def signin():
    with app.app_context():
        return UserManagement.signin()
    return "Sign in"

@app.route('/signout')
def signout():
    with app.app_context():
        return UserManagement.signout()
    return "Sign out"

if __name__ == '__main__':
    app.run(debug=True, port=0)