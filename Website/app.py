# =[Modules dan Packages]========================

from flask import Flask,render_template,request,jsonify
import json
from werkzeug.utils import secure_filename
import pyrebase
from datetime import datetime, timedelta
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import os
import matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style="whitegrid")
import warnings
warnings.filterwarnings("ignore")
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM #, RNN, GRU
from sklearn.model_selection import GridSearchCV
from tensorflow.keras.wrappers.scikit_learn import KerasRegressor
from tensorflow.keras.callbacks import EarlyStopping
import pickle

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

def biaya(daya, kwh):
    if daya <= 900:
        return kwh * 1352
    elif daya <= 1300 or daya <= 2200:
        return kwh * 1467
    elif daya <= 3500 or daya <= 5500:
        return kwh * 1699

def compute_fuzzy(waktu, kwh, daya, biaya, tanggal):
  dir = f'static/assets/img/fuzzy_result/{tanggal}'
  if not os.path.exists(dir):
      os.makedirs(dir)
  
  waktu_variabel = ctrl.Antecedent(np.arange(0,24,1), "waktu")
  kwh_variabel = ctrl.Antecedent(np.arange(0,7,1), "kwh")
  daya_variabel = ctrl.Antecedent(np.arange(0,2200,1), "daya")
  biaya_variabel = ctrl.Antecedent(np.arange(-20000,20000,1), "biaya")
  penggunaan_listrik_variabel = ctrl.Consequent(np.arange(0,100,1), "penggunaan_listrik")

  waktu_variabel["Cepat"] = fuzz.trapmf(waktu_variabel.universe, [0,0,6,8])
  waktu_variabel["Normal"] = fuzz.trapmf(waktu_variabel.universe, [6,8,10,12])
  waktu_variabel["Lama"] = fuzz.trapmf(waktu_variabel.universe, [10,12,24,24])

  kwh_variabel["Rendah"] = fuzz.trapmf(kwh_variabel.universe, [0,0,2,3])
  kwh_variabel["Normal"] = fuzz.trimf(kwh_variabel.universe, [2,3,4])
  kwh_variabel["Tinggi"] = fuzz.trapmf(kwh_variabel.universe, [3,4,7,7])

  daya_variabel["Rendah"] = fuzz.trapmf(daya_variabel.universe, [0,0,900,1300])
  daya_variabel["Normal"] = fuzz.trimf(daya_variabel.universe, [900,1300,2200])
  daya_variabel["Tinggi"] = fuzz.trimf(daya_variabel.universe, [1300,2200,2200])

  biaya_variabel["Murah"] = fuzz.trapmf(biaya_variabel.universe, [-20000, -20000,-7000,-3000])
  biaya_variabel["Normal"] = fuzz.trapmf(biaya_variabel.universe, [-7000, -3000,3000,7000])
  biaya_variabel["Mahal"] = fuzz.trapmf(biaya_variabel.universe, [3000,7000,20000,20000])

  penggunaan_listrik_variabel["Hemat"] = fuzz.trapmf(penggunaan_listrik_variabel.universe, [0,0,30,50])
  penggunaan_listrik_variabel["Normal"] = fuzz.trimf(penggunaan_listrik_variabel.universe, [40,55,70])
  penggunaan_listrik_variabel["Boros"] = fuzz.trapmf(penggunaan_listrik_variabel.universe, [60,80,100,100])

  # waktu_variabel.view()
  # kwh_variabel.view()
  # daya_variabel.view()
  # biaya_variabel.view()
  # penggunaan_listrik_variabel.view()

  rule1 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Rendah"] & daya_variabel["Rendah"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Hemat"])
  rule2 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Rendah"] & daya_variabel["Rendah"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Hemat"])
  rule3 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Rendah"] & daya_variabel["Rendah"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Hemat"])
  rule4 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Rendah"] & daya_variabel["Normal"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Hemat"])
  rule5 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Rendah"] & daya_variabel["Normal"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Hemat"])
  rule6 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Rendah"] & daya_variabel["Normal"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Normal"])
  rule7 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Rendah"] & daya_variabel["Tinggi"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Hemat"])
  rule8 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Rendah"] & daya_variabel["Tinggi"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Normal"])
  rule9 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Rendah"] & daya_variabel["Tinggi"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Normal"])
  rule10 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Normal"] & daya_variabel["Rendah"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Hemat"])
  rule11 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Normal"] & daya_variabel["Rendah"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Hemat"])
  rule12 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Normal"] & daya_variabel["Rendah"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Normal"])
  rule13 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Normal"] & daya_variabel["Normal"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Normal"])
  rule14 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Normal"] & daya_variabel["Normal"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Normal"])
  rule15 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Normal"] & daya_variabel["Normal"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Normal"])
  rule16 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Normal"] & daya_variabel["Tinggi"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Normal"])
  rule17 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Normal"] & daya_variabel["Tinggi"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Normal"])
  rule18 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Normal"] & daya_variabel["Tinggi"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Normal"])
  rule19 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Tinggi"] & daya_variabel["Rendah"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Normal"])
  rule20 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Tinggi"] & daya_variabel["Rendah"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Boros"])
  rule21 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Tinggi"] & daya_variabel["Rendah"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Boros"])
  rule22 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Tinggi"] & daya_variabel["Normal"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Boros"])
  rule23 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Tinggi"] & daya_variabel["Normal"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Boros"])
  rule24 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Tinggi"] & daya_variabel["Normal"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Boros"])
  rule25 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Tinggi"] & daya_variabel["Tinggi"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Boros"])
  rule26 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Tinggi"] & daya_variabel["Tinggi"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Boros"])
  rule27 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Tinggi"] & daya_variabel["Tinggi"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Boros"])
  rule28 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Rendah"] & daya_variabel["Rendah"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Hemat"])
  rule29 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Rendah"] & daya_variabel["Rendah"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Hemat"])
  rule30 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Rendah"] & daya_variabel["Rendah"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Hemat"])
  rule31 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Rendah"] & daya_variabel["Normal"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Hemat"])
  rule32 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Rendah"] & daya_variabel["Normal"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Hemat"])
  rule33 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Rendah"] & daya_variabel["Normal"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Hemat"])
  rule34 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Rendah"] & daya_variabel["Tinggi"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Normal"])
  rule35 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Rendah"] & daya_variabel["Tinggi"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Normal"])
  rule36 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Rendah"] & daya_variabel["Tinggi"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Normal"])
  rule37 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Normal"] & daya_variabel["Rendah"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Hemat"])
  rule38 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Normal"] & daya_variabel["Rendah"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Normal"])
  rule39 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Normal"] & daya_variabel["Rendah"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Normal"])
  rule40 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Normal"] & daya_variabel["Normal"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Normal"])
  rule41 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Normal"] & daya_variabel["Normal"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Normal"])
  rule42 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Normal"] & daya_variabel["Normal"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Normal"])
  rule43 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Normal"] & daya_variabel["Tinggi"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Normal"])
  rule44 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Normal"] & daya_variabel["Tinggi"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Normal"])
  rule45 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Normal"] & daya_variabel["Tinggi"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Normal"])
  rule46 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Tinggi"] & daya_variabel["Rendah"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Normal"])
  rule47 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Tinggi"] & daya_variabel["Rendah"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Boros"])
  rule48 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Tinggi"] & daya_variabel["Rendah"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Boros"])
  rule49 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Tinggi"] & daya_variabel["Normal"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Boros"])
  rule50 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Tinggi"] & daya_variabel["Normal"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Boros"])
  rule51 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Tinggi"] & daya_variabel["Normal"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Boros"])
  rule52 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Tinggi"] & daya_variabel["Tinggi"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Boros"])
  rule53 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Tinggi"] & daya_variabel["Tinggi"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Boros"])
  rule54 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Tinggi"] & daya_variabel["Tinggi"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Boros"])
  rule55 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Rendah"] & daya_variabel["Rendah"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Hemat"])
  rule56 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Rendah"] & daya_variabel["Rendah"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Hemat"])
  rule57 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Rendah"] & daya_variabel["Rendah"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Hemat"])
  rule58 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Rendah"] & daya_variabel["Normal"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Hemat"])
  rule59 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Rendah"] & daya_variabel["Normal"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Hemat"])
  rule60 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Rendah"] & daya_variabel["Normal"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Hemat"])
  rule61 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Rendah"] & daya_variabel["Tinggi"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Hemat"])
  rule62 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Rendah"] & daya_variabel["Tinggi"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Hemat"])
  rule63 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Rendah"] & daya_variabel["Tinggi"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Hemat"])
  rule64 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Normal"] & daya_variabel["Rendah"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Hemat"])
  rule65 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Normal"] & daya_variabel["Rendah"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Hemat"])
  rule66 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Normal"] & daya_variabel["Rendah"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Hemat"])
  rule67 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Normal"] & daya_variabel["Normal"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Hemat"])
  rule68 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Normal"] & daya_variabel["Normal"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Hemat"])
  rule69 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Normal"] & daya_variabel["Normal"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Hemat"])
  rule70 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Normal"] & daya_variabel["Tinggi"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Normal"])
  rule71 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Normal"] & daya_variabel["Tinggi"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Normal"])
  rule72 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Normal"] & daya_variabel["Tinggi"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Normal"])
  rule73 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Tinggi"] & daya_variabel["Rendah"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Normal"])
  rule74 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Tinggi"] & daya_variabel["Rendah"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Hemat"])
  rule75 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Tinggi"] & daya_variabel["Rendah"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Normal"])
  rule76 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Tinggi"] & daya_variabel["Normal"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Normal"])
  rule77 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Tinggi"] & daya_variabel["Normal"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Boros"])
  rule78 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Tinggi"] & daya_variabel["Normal"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Boros"])
  rule79 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Tinggi"] & daya_variabel["Tinggi"] & biaya_variabel["Murah"], penggunaan_listrik_variabel["Boros"])
  rule80 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Tinggi"] & daya_variabel["Tinggi"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Boros"])
  rule81 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Tinggi"] & daya_variabel["Tinggi"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Boros"])

  rule_list = [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20, rule21, rule22, rule23, rule24, rule25, rule26, rule27, rule28, rule29, rule30, rule31, rule32, rule33, rule34, rule35, rule36, rule37, rule38, rule39, rule40, rule41, rule42, rule43, rule44, rule45, rule46, rule47, rule48, rule49, rule50, rule51, rule52, rule53, rule54, rule55, rule56, rule57, rule58, rule59, rule60, rule61, rule62, rule63, rule64, rule65, rule66, rule67, rule68, rule69, rule70, rule71, rule72, rule73, rule74, rule75, rule76, rule77, rule78, rule79, rule80, rule81]

  penggunaan_listrik_ctrl = ctrl.ControlSystem(rule_list)
  perf_analysis = ctrl.ControlSystemSimulation(penggunaan_listrik_ctrl)

  perf_analysis.input["waktu"] = waktu
  perf_analysis.input["kwh"] = kwh
  perf_analysis.input["daya"] = daya
  perf_analysis.input["biaya"] = biaya

  perf_analysis.compute()
  output = round(perf_analysis.output["penggunaan_listrik"],2)
  print(perf_analysis.output['penggunaan_listrik'])

  matplotlib.use('Agg')
  waktu_variabel.view(sim=perf_analysis)
  plt.savefig(f'{dir}/waktu.png')
  plt.close()

  matplotlib.use('Agg')
  kwh_variabel.view(sim=perf_analysis)
  plt.savefig(f'{dir}/energi.png')
  plt.close()

  matplotlib.use('Agg')
  daya_variabel.view(sim=perf_analysis)
  plt.savefig(f'{dir}/daya.png')
  plt.close()

  matplotlib.use('Agg')
  biaya_variabel.view(sim=perf_analysis)
  plt.savefig(f'{dir}/biaya.png')
  plt.close()

  matplotlib.use('Agg')
  penggunaan_listrik_variabel.view(sim=perf_analysis)
  plt.savefig(f'{dir}/penggunaan_listrik.png')
  plt.close()

  print("ini outputnya :", output)
  
  return output

def defuzzifikasi_result(fuzzy_value):
	if fuzzy_value <=33:
		return "Hemat"
	elif fuzzy_value >33 and fuzzy_value <=45:
		return "Normal"
	elif fuzzy_value>45:
		return "Boros"

def get_rentang_tanggal(tanggal_awal, tanggal_akhir, data):
	# Tanggal awal dan akhir
	tanggal_awal_temp = datetime.strptime(tanggal_awal, '%d-%m-%Y')
	tanggal_akhir_temp = datetime.strptime(tanggal_akhir, '%d-%m-%Y')

  # List untuk menyimpan tanggal
	list_tanggal = []

  # Loop untuk mengisi list dengan tanggal-tanggal di antara tanggal awal dan akhir
	tanggal = tanggal_awal_temp
	while tanggal <= tanggal_akhir_temp:
		# print(tanggal, type(tanggal.strftime('%d-%m-%Y')), "INIIIIII TYPE NYAAAAA")
		list_tanggal.append(tanggal.strftime('%d-%m-%Y'))
		tanggal += timedelta(days=1)
  
	list_iris = []
  
	for tanggal in list_tanggal:
		if tanggal in data.val():
			list_iris.append(tanggal)
	return list_iris

# def kurang_satu(angka):
# 	angka_kurang_satu = str(int(angka) - 1).zfill(2)
# 	return angka_kurang_satu

def kurang_satu(tanggal_string):
	# tanggal_string = '02-02-2024'
	tanggal = datetime.strptime(tanggal_string, '%d-%m-%Y')
	tanggal_sebulan_sebelumnya = tanggal - timedelta(days=30)
	tanggal_sebulan_sebelumnya_string = tanggal_sebulan_sebelumnya.strftime('%d-%m-%Y')
	return tanggal_sebulan_sebelumnya_string

def get_selisih_biaya(tanggal_akhir, data):
	biaya_bulan_lalu, biaya_bulan_ini = [],[]
	split_date = tanggal_akhir.split("-")
	
	tanggal_awal = f"01-{split_date[1]}-{split_date[2]}"
	bulan_ini = get_rentang_tanggal(tanggal_awal, tanggal_akhir, data)
	
	tanggal_awal = kurang_satu(tanggal_awal)
	tanggal_akhir = kurang_satu(tanggal_akhir)
	bulan_lalu = get_rentang_tanggal(tanggal_awal, tanggal_akhir, data)
	
	for bulan in bulan_ini:
		coll =  db.child(f"/collection_data/electricity_data/{bulan}").get()
		biaya_bulan_ini.append(float(coll.val()["biaya"]))
	
	for bulan in bulan_lalu:
		coll =  db.child(f"/collection_data/electricity_data/{bulan}").get()
		biaya_bulan_lalu.append(float(coll.val()["biaya"]))
	
	# print("s")
	return int((sum(biaya_bulan_ini)/len(biaya_bulan_ini))-(sum(biaya_bulan_lalu)/len(biaya_bulan_lalu)))

def load_model_ai():
	# models
	file_pickle = 'static/models/best_model.pkl'
  # Membuka kembali file pickle
	with open(file_pickle, 'rb') as file:
		best_model = pickle.load(file)
	
  # train
	file_pickle = 'static/models/train.pkl'
	# Membuka kembali file pickle
	with open(file_pickle, 'rb') as file:
		train = pickle.load(file)

	# test
	file_pickle = 'static/models/test.pkl'
	# Membuka kembali file pickle
	with open(file_pickle, 'rb') as file:
		test = pickle.load(file)
	
	return best_model, train, test

# =[Variabel Global]=============================
app = Flask(__name__, static_url_path='/static')

# =[Routing]=====================================
# [Routing untuk Halaman login]
@app.route("/")
def login():
	return render_template('login.html')

#[Routing untuk Halaman Utama atau Home]
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		if username == "admin1234" and password == "admin1234":
			return render_template('index.html')
	else:
		print("Tidak ada input stroom token.")
		return render_template('login.html')

#[Routing untuk Halaman Utama atau Home]
@app.route("/beranda")
def beranda():
	return render_template('index.html')

# [Routing untuk Halaman Fuzzy Analysis]
@app.route("/fuzzy_analisis")
def fuzzy_analisis():
	return render_template('fuzzy_analisis.html')

# [Routing untuk Halaman AI Tools]
@app.route("/ai_tools")
def ai_tools():
	return render_template('ai_tools.html')

# [Routing untuk Input Token]
@app.route("/api/input_token", methods=['POST'])
def token():
	if request.method == 'POST':
		stroom_token = request.json['stroom_token']
		print(stroom_token)
		
		db.child("/collection_data/tokenizer").update({"stroom_token":stroom_token})
	else:
			print("Tidak ada input stroom token.")

	return jsonify({"status": stroom_token})

# [Routing untuk forcesting]	
@app.route("/api/forcesting",methods=['POST'])
def forcesting():
	best_model, train, test = load_model_ai()
	# rentang_tanggal, rentang_kwh, rentang_daya, rentang_biaya, rentang_timestamp, defuzzifikasi, data_dict_list, value = [],[],[],[],[],[],[],[]
	# flag = False
	if request.method == 'POST':
		window_size = 14
		tanggal_forcest = datetime.strptime(request.json['tanggal_forcest'], "%Y-%m-%d")
		tanggal_awal = datetime.strptime('2024-03-06', '%Y-%m-%d')

		today_str = datetime.now().strftime('%Y-%m-%d')
		# Parsing string tanggal ke objek datetime
		today_datetime = datetime.strptime(today_str, '%Y-%m-%d')
		
		selisih_hari_prediksi = (tanggal_forcest - tanggal_awal).days
		selisih_hari_jumlah = (tanggal_forcest - today_datetime).days

		
		scaler = StandardScaler()
		scaler.fit_transform(train[['biaya']])

		train['scaled'] = scaler.transform(train[['biaya']])
		test['scaled'] = scaler.transform(test[['biaya']])
		n_future = "30" #@param {type:"string"}

		# forecasting data selanjutnya
		y_train = scaler.transform(train[['biaya']])
		# n_future = int(n_future) # hari kedepan
		n_future = int(selisih_hari_prediksi) # hari kedepan
		future = [[y_train[-1,0]]]
		X_new = y_train[-window_size:,0].tolist()

		for i in range(n_future):
			y_future = best_model.predict(np.array([X_new]).reshape(1,window_size,1))
			future.append([y_future[0,0]])
			X_new = X_new[1:]
			X_new.append(y_future[0,0])

		future = scaler.inverse_transform(np.array(future))
		date_future = pd.date_range(start=train['tanggal'].values[-1], periods=n_future+1, freq='D')
		hasil = f"{'{:,.0f}'.format(int(sum(future[selisih_hari_prediksi-selisih_hari_jumlah:,0]))).replace(',', '.')}"
		print("INI HASIL : ", hasil)
		print("type date_future:", type(date_future))
		print(date_future[1])
		print("type future:", type(future))
		print(future[1][0])


		# tanggal_akhir = request.json['tanggal_akhir']

		# tanggal_awal = str(datetime.strptime(request.json['tanggal_awal'], "%Y-%m-%d").strftime("%d-%m-%Y"))
		# tanggal_akhir = str(datetime.strptime(request.json['tanggal_akhir'], "%Y-%m-%d").strftime("%d-%m-%Y"))

		# # Mendapatkan data dari root node
		# data = db.child("/collection_data/electricity_data/").get()

		# list_iris = get_rentang_tanggal(tanggal_awal,tanggal_akhir, data)

		# # Konversi kembali set menjadi list jika perlu
		# # list_iris = list(iris)
		# print("-------------------")
		# print(list_iris)
		# print("-------------------")

		# # Memeriksa apakah data berhasil diambil
		# if tanggal_awal in list_iris and tanggal_akhir in list_iris:
		# 	# Iterasi melalui nama-nama child
		# 	for child_name in list_iris:
		# 		print(child_name)
		# 		selisih_biaya = get_selisih_biaya(child_name, data)
		# 		# print("INII TYPE CHILD NYA: ", type(child_name))
		# 		if child_name == tanggal_awal:
		# 			flag=True
		# 		if child_name == tanggal_akhir:
		# 			flag=False
		# 			# GET data from Firebase
		# 			coll =  db.child(f"/collection_data/electricity_data/{child_name}").get()
		# 			result_fuzzy = compute_fuzzy(int(coll.val()["timestamp"].split(":")[0]), coll.val()["kwh"], coll.val()["daya"], selisih_biaya, child_name)
		# 			rentang_kwh.append(coll.val()["kwh"])
		# 			rentang_daya.append(coll.val()["daya"])
		# 			rentang_biaya.append(selisih_biaya)
		# 			rentang_timestamp.append(coll.val()["timestamp"])
		# 			value.append(result_fuzzy)
		# 			defuzzifikasi.append(defuzzifikasi_result(result_fuzzy))
		# 			rentang_tanggal.append(child_name)
		# 		if flag==True:
		# 			coll =  db.child(f"/collection_data/electricity_data/{child_name}").get()
		# 			result_fuzzy = compute_fuzzy(int(coll.val()["timestamp"].split(":")[0]), coll.val()["kwh"], coll.val()["daya"], selisih_biaya, child_name)
		# 			rentang_kwh.append(coll.val()["kwh"])
		# 			rentang_daya.append(coll.val()["daya"])
		# 			rentang_biaya.append(selisih_biaya)
		# 			rentang_timestamp.append(coll.val()["timestamp"])
		# 			value.append(result_fuzzy)
		# 			defuzzifikasi.append(defuzzifikasi_result(result_fuzzy))
		# 			rentang_tanggal.append(child_name)
		# else:
		# 	print("Tanggal tidak ada data di database.")

		# # Menampilkan hasil
		# print(f"Tanggal Awal : {tanggal_awal}")
		# print(f"Tanggal Akhir : {tanggal_akhir}")
		# for tgl in rentang_tanggal:
		# 	print(f"Tanggal yang tersedia : {tgl}")
		
		
		data_dict_list = []
		
		for i in range(len(date_future)):
			data_dict = {
				"biaya": hasil,
				"tanggal": str(datetime.strptime(str(date_future[i]), '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')),
				"estimasi": future[i][0]
			}
			data_dict_list.append(data_dict)
	return jsonify(data_dict_list)

# [Routing untuk fuzzy]	
@app.route("/api/fuzzyLogic",methods=['POST'])
def fuzzy():
	rentang_tanggal, rentang_kwh, rentang_daya, rentang_biaya, rentang_timestamp, defuzzifikasi, data_dict_list, value = [],[],[],[],[],[],[],[]
	flag = False
	if request.method == 'POST':
		tanggal_awal = request.json['tanggal_awal']
		tanggal_akhir = request.json['tanggal_akhir']

		tanggal_awal = str(datetime.strptime(request.json['tanggal_awal'], "%Y-%m-%d").strftime("%d-%m-%Y"))
		tanggal_akhir = str(datetime.strptime(request.json['tanggal_akhir'], "%Y-%m-%d").strftime("%d-%m-%Y"))

		# Mendapatkan data dari root node
		data = db.child("/collection_data/electricity_data/").get()

		list_iris = get_rentang_tanggal(tanggal_awal,tanggal_akhir, data)

		# Konversi kembali set menjadi list jika perlu
		# list_iris = list(iris)
		print("-------------------")
		print(list_iris)
		print("-------------------")

		# Memeriksa apakah data berhasil diambil
		if tanggal_awal in list_iris and tanggal_akhir in list_iris:
			# Iterasi melalui nama-nama child
			for child_name in list_iris:
				print(child_name)
				selisih_biaya = get_selisih_biaya(child_name, data)
				print("ini selisih nya: ", selisih_biaya)
				# print("INII TYPE CHILD NYA: ", type(child_name))
				if child_name == tanggal_awal:
					flag=True
				if child_name == tanggal_akhir:
					flag=False
					# GET data from Firebase
					coll =  db.child(f"/collection_data/electricity_data/{child_name}").get()
					result_fuzzy = compute_fuzzy(int(coll.val()["timestamp"].split(":")[0]), coll.val()["kwh"], coll.val()["daya"], selisih_biaya, child_name)
					rentang_kwh.append(coll.val()["kwh"])
					rentang_daya.append(coll.val()["daya"])
					rentang_biaya.append(selisih_biaya)
					rentang_timestamp.append(coll.val()["timestamp"])
					value.append(result_fuzzy)
					defuzzifikasi.append(defuzzifikasi_result(result_fuzzy))
					rentang_tanggal.append(child_name)
				if flag==True:
					coll =  db.child(f"/collection_data/electricity_data/{child_name}").get()
					result_fuzzy = compute_fuzzy(int(coll.val()["timestamp"].split(":")[0]), coll.val()["kwh"], coll.val()["daya"], selisih_biaya, child_name)
					rentang_kwh.append(coll.val()["kwh"])
					rentang_daya.append(coll.val()["daya"])
					rentang_biaya.append(selisih_biaya)
					rentang_timestamp.append(coll.val()["timestamp"])
					value.append(result_fuzzy)
					defuzzifikasi.append(defuzzifikasi_result(result_fuzzy))
					rentang_tanggal.append(child_name)
		else:
			print("Tanggal tidak ada data di database.")

		# Menampilkan hasil
		print(f"Tanggal Awal : {tanggal_awal}")
		print(f"Tanggal Akhir : {tanggal_akhir}")
		for tgl in rentang_tanggal:
			print(f"Tanggal yang tersedia : {tgl}")
		
		
		for i in range(len(rentang_tanggal)):
			data_dict = {
				"tanggal": rentang_tanggal[i],
				"kwh": rentang_kwh[i],
				"daya": rentang_daya[i],
				"biaya": rentang_biaya[i],
				"timestamp": rentang_timestamp[i],
				"value": value[i],
				"defuzzifikasi": defuzzifikasi[i]
			}
			data_dict_list.append(data_dict)
	return jsonify(data_dict_list)

	

# =[Main]========================================		

if __name__ == '__main__':
	# Run Flask di localhost 
	app.run(host="localhost", port=5000, debug=True)

	# firebase = pyrebase.initialize_app(config)
	# db = firebase.database()

	# # Push Data to Firebase
	# db.child("Test/names").set({"Nama":"Dastin Aryo Atmanto"})

	# # Update Data to Firebase
	# db.child("Test/names").update({"Nama":"Ghernald"})

	# # Remove data to Firebase
	# # db.child("Test").remove()

	# # GET data from Firebase
	# users =  db.child("Test/names").get()
	# print(users.val()["Nama"])