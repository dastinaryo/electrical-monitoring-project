# =[Modules dan Packages]========================

from flask import Flask,render_template,request,jsonify
import json
from werkzeug.utils import secure_filename
import pyrebase
from datetime import datetime
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def ekspor(path):
    # Database Electrical Project
    config = {
      "apiKey": "AIzaSyBUpK_rPmyscqQWoCIEhonsMJ_wXLyy8h0",
      "authDomain": "electrical-project-8def2.firebaseapp.com",
      "databaseURL": "https://electrical-project-8def2-default-rtdb.asia-southeast1.firebasedatabase.app",
      "projectId": "electrical-project-8def2",
      "storageBucket": "electrical-project-8def2.appspot.com",
      "messagingSenderId": "511048889856",
      "appId": "1:511048889856:web:62f75f26c6ee5741540ae5"
    }

    firebase = pyrebase.initialize_app(config)
    db = firebase.database()

    # Mendapatkan seluruh data dari node
    all_children = db.get().val()

    # Simpan data ke dalam file JSON
    with open(path, "w") as json_file:
        json.dump(all_children, json_file, indent=4)

    print("Data berhasil disimpan dalam output.json")

def impor(path):
    # Database Electrical IoT
    # config = {
    #   "apiKey": "AIzaSyAvAR2K7jM62Eeyr8Ys6J4SmE8iVK0574Q",
    #   "authDomain": "electrical-iot.firebaseapp.com",
    #   "databaseURL": "https://electrical-iot-default-rtdb.asia-southeast1.firebasedatabase.app",
    #   "projectId": "electrical-iot",
    #   "storageBucket": "electrical-iot.appspot.com",
    #   "messagingSenderId": "10658435258",
    #   "appId": "1:10658435258:web:a8ede605e0e4b29088b283"
    # }

    config = {
      "apiKey": "AIzaSyBUpK_rPmyscqQWoCIEhonsMJ_wXLyy8h0",
      "authDomain": "electrical-project-8def2.firebaseapp.com",
      "databaseURL": "https://electrical-project-8def2-default-rtdb.asia-southeast1.firebasedatabase.app",
      "projectId": "electrical-project-8def2",
      "storageBucket": "electrical-project-8def2.appspot.com",
      "messagingSenderId": "511048889856",
      "appId": "1:511048889856:web:62f75f26c6ee5741540ae5"
    }


    firebase = pyrebase.initialize_app(config)
    db = firebase.database()


    # Baca data dari file JSON
    with open(path, "r") as json_file:
        data_to_write = json.load(json_file)

    # Tulis data ke Realtime Database
    db.set(data_to_write)

    print("Data berhasil ditulis ke Realtime Database")

# ekspor("database_fix_non-anomally.json")
impor("database_fix_non-anomally.json")