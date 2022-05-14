from flask import Flask, request
import Modules.Utils as Utils
import Modules.UserManagement as UserManagement

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
        managedData = Utils.getData();
        #TO DO: algoritem, ki ti vrne random ime
        
    return "Izpis random imena"
    
    
@app.route('/userinfo')
def userinfo():
    with app.app_context():
        return UserManagement.userinfo()
    return "User info"

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
    app.run(debug=True)