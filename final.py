from flask import Flask, jsonify, request
from pymodm import connect, MongoModel, fields
from datetime import datetime

connect("mongodb://sputney13:sputney13@ds161901.mlab.com:61901/bme590final")
app = Flask(__name__)
app.run(host="127.0.0.1")
