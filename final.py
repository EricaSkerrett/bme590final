from flask import Flask, jsonify, request
from pymodm import connect, MongoModel, fields
from datetime import datetime

connect("mongodb://sputney13:sputney13@ds161901.mlab.com:61901/bme590final")
app = Flask(__name__)
app.run(host="127.0.0.1")


class Image(MongoModel):
    user = fields.IntegerField(primary_key=True)
    uploaded_images = fields.ListField(field=fields.ImageField())
    upload_times = fields.ListField(field=fields.DateTimeField())
    processed_images = fields.ListField(field=fields.ImageField())
    process_types = fields.ListField(field=fields.CharField())
    process_times = fields.ListField(field=fields.DateTimeField())
    user_metrics = fields.DictField()
