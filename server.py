from flask import Flask
import Modules.Utils as Utils

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/getNextName')
def returnName():
    with app.app_context():
        managedData = Utils.getData();
        #TO DO: algoritem, ki ti vrne najprimernejše ime
        
    return "Izpis imena"