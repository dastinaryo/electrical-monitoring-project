# =[Modules dan Packages]========================

from flask import Flask,render_template,request,jsonify
import json
from werkzeug.utils import secure_filename
import pyrebase
from datetime import datetime
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import os
import matplotlib

config = {
  "apiKey": "apiKey",
  "authDomain": "authDomain",
  "databaseURL": "databaseURL",
  "projectId": "projectId",
  "storageBucket": "storageBucket",
  "messagingSenderId": "messagingSenderId",
  "appId": "appId"
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
  biaya_variabel = ctrl.Antecedent(np.arange(0,30000,1), "biaya")
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

  biaya_variabel["Normal"] = fuzz.trapmf(biaya_variabel.universe, [0,0,7600,13000])
  biaya_variabel["Mahal"] = fuzz.trapmf(biaya_variabel.universe, [7600,13000,30000,30000])

  penggunaan_listrik_variabel["Hemat"] = fuzz.trapmf(penggunaan_listrik_variabel.universe, [0,0,30,50])
  penggunaan_listrik_variabel["Normal"] = fuzz.trimf(penggunaan_listrik_variabel.universe, [40,55,70])
  penggunaan_listrik_variabel["Boros"] = fuzz.trapmf(penggunaan_listrik_variabel.universe, [60,80,100,100])

  rule1 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Rendah"] & daya_variabel["Rendah"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Hemat"])
  rule2 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Rendah"] & daya_variabel["Rendah"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Hemat"])
  rule3 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Rendah"] & daya_variabel["Normal"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Hemat"])
  rule4 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Rendah"] & daya_variabel["Normal"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Hemat"])
  rule5 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Rendah"] & daya_variabel["Tinggi"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Hemat"])
  rule6 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Rendah"] & daya_variabel["Tinggi"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Hemat"])
  rule7 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Normal"] & daya_variabel["Rendah"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Normal"])
  rule8 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Normal"] & daya_variabel["Rendah"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Normal"])
  rule9 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Normal"] & daya_variabel["Normal"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Normal"])
  rule10 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Normal"] & daya_variabel["Normal"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Normal"])
  rule11 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Normal"] & daya_variabel["Tinggi"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Normal"])
  rule12 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Normal"] & daya_variabel["Tinggi"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Normal"])
  rule13 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Tinggi"] & daya_variabel["Rendah"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Boros"])
  rule14 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Tinggi"] & daya_variabel["Rendah"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Boros"])
  rule15 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Tinggi"] & daya_variabel["Normal"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Boros"])
  rule16 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Tinggi"] & daya_variabel["Normal"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Boros"])
  rule17 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Tinggi"] & daya_variabel["Tinggi"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Boros"])
  rule18 = ctrl.Rule(waktu_variabel["Cepat"] & kwh_variabel["Tinggi"] & daya_variabel["Tinggi"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Boros"])
  rule19 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Rendah"] & daya_variabel["Rendah"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Hemat"])
  rule20 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Rendah"] & daya_variabel["Rendah"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Hemat"])
  rule21 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Rendah"] & daya_variabel["Normal"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Hemat"])
  rule22 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Rendah"] & daya_variabel["Normal"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Hemat"])
  rule23 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Rendah"] & daya_variabel["Tinggi"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Hemat"])
  rule24 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Rendah"] & daya_variabel["Tinggi"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Hemat"])
  rule25 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Normal"] & daya_variabel["Rendah"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Normal"])
  rule26 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Normal"] & daya_variabel["Rendah"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Normal"])
  rule27 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Normal"] & daya_variabel["Normal"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Normal"])
  rule28 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Normal"] & daya_variabel["Normal"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Normal"])
  rule29 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Normal"] & daya_variabel["Tinggi"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Normal"])
  rule30 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Normal"] & daya_variabel["Tinggi"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Normal"])
  rule31 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Tinggi"] & daya_variabel["Rendah"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Boros"])
  rule32 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Tinggi"] & daya_variabel["Rendah"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Boros"])
  rule33 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Tinggi"] & daya_variabel["Normal"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Boros"])
  rule34 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Tinggi"] & daya_variabel["Normal"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Boros"])
  rule35 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Tinggi"] & daya_variabel["Tinggi"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Boros"])
  rule36 = ctrl.Rule(waktu_variabel["Normal"] & kwh_variabel["Tinggi"] & daya_variabel["Tinggi"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Boros"])
  rule37 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Rendah"] & daya_variabel["Rendah"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Hemat"])
  rule38 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Rendah"] & daya_variabel["Rendah"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Hemat"])
  rule39 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Rendah"] & daya_variabel["Normal"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Hemat"])
  rule40 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Rendah"] & daya_variabel["Normal"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Hemat"])
  rule41 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Rendah"] & daya_variabel["Tinggi"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Hemat"])
  rule42 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Rendah"] & daya_variabel["Tinggi"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Hemat"])
  rule43 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Normal"] & daya_variabel["Rendah"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Normal"])
  rule44 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Normal"] & daya_variabel["Rendah"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Normal"])
  rule45 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Normal"] & daya_variabel["Normal"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Normal"])
  rule46 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Normal"] & daya_variabel["Normal"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Normal"])
  rule47 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Normal"] & daya_variabel["Tinggi"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Normal"])
  rule48 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Normal"] & daya_variabel["Tinggi"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Normal"])
  rule49 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Tinggi"] & daya_variabel["Rendah"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Boros"])
  rule50 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Tinggi"] & daya_variabel["Rendah"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Boros"])
  rule51 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Tinggi"] & daya_variabel["Normal"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Boros"])
  rule52 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Tinggi"] & daya_variabel["Normal"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Boros"])
  rule53 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Tinggi"] & daya_variabel["Tinggi"] & biaya_variabel["Normal"], penggunaan_listrik_variabel["Boros"])
  rule54 = ctrl.Rule(waktu_variabel["Lama"] & kwh_variabel["Tinggi"] & daya_variabel["Tinggi"] & biaya_variabel["Mahal"], penggunaan_listrik_variabel["Boros"])

  rule_list = [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20, rule21, rule22, rule23, rule24, rule25, rule26, rule27, rule28, rule29, rule30, rule31, rule32, rule33, rule34, rule35, rule36, rule37, rule38, rule39, rule40, rule41, rule42, rule43, rule44, rule45, rule46, rule47, rule48, rule49, rule50, rule51, rule52, rule53, rule54]

  penggunaan_listrik_ctrl = ctrl.ControlSystem(rule_list)
  perf_analysis = ctrl.ControlSystemSimulation(penggunaan_listrik_ctrl)

  perf_analysis.input["waktu"] = waktu
  perf_analysis.input["kwh"] = kwh
  perf_analysis.input["daya"] = daya
  perf_analysis.input["biaya"] = biaya
  
  perf_analysis.compute()
  output = round(perf_analysis.output["penggunaan_listrik"],2)

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
  
  return output

def defuzzifikasi_result(fuzzy_value):
	if fuzzy_value <=33:
		return "Hemat"
	elif fuzzy_value >33 and fuzzy_value <=45:
		return "Normal"
	elif fuzzy_value>45:
		return "Boros"


# =[Variabel Global]=============================
app = Flask(__name__, static_url_path='/static')

# =[Routing]=====================================
# [Routing untuk Halaman Utama atau Home]
@app.route("/")
def beranda():
	return render_template('index.html')


@app.route("/fuzzy_analisis")
def fuzzy_analisis():
	return render_template('fuzzy_analisis.html')


@app.route("/api/input_token", methods=['POST'])
def token():
	if request.method == 'POST':
		stroom_token = request.json['stroom_token']
		print(stroom_token)
		
		db.child("/collection_data/tokenizer").update({"stroom_token":stroom_token})
	else:
			print("Tidak ada input stroom token.")

	return jsonify({"status": stroom_token})

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
		data = db.child("/collection_data/electricity data/").get()

		for child_name in data.val():
			print(child_name)

		# Memeriksa apakah data berhasil diambil
		if tanggal_awal in data.val() and tanggal_akhir in data.val():
			# Iterasi melalui nama-nama child
			for child_name in data.val():
				if child_name == tanggal_awal:
					flag=True
				if child_name == tanggal_akhir:
					flag=False
					# GET data from Firebase
					coll =  db.child(f"/collection_data/electricity data/{child_name}").get()
					result_fuzzy = compute_fuzzy(int(coll.val()["timestamp"].split(":")[0]), coll.val()["kwh"], coll.val()["daya"], coll.val()["biaya"], child_name)
					rentang_kwh.append(coll.val()["kwh"])
					rentang_daya.append(coll.val()["daya"])
					rentang_biaya.append(coll.val()["biaya"])
					rentang_timestamp.append(coll.val()["timestamp"])
					value.append(result_fuzzy)
					defuzzifikasi.append(defuzzifikasi_result(result_fuzzy))
					rentang_tanggal.append(child_name)
				if flag==True:
					coll =  db.child(f"/collection_data/electricity data/{child_name}").get()
					result_fuzzy = compute_fuzzy(int(coll.val()["timestamp"].split(":")[0]), coll.val()["kwh"], coll.val()["daya"], coll.val()["biaya"], child_name)
					rentang_kwh.append(coll.val()["kwh"])
					rentang_daya.append(coll.val()["daya"])
					rentang_biaya.append(coll.val()["biaya"])
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