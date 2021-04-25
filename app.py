from flask import Flask, render_template, request, redirect, url_for,session
import pandas as pd 
import json
import mysql.connector
from chefboost import Chefboost as chef
from sklearn.model_selection import train_test_split
from collections import Counter
import numpy as np

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="esportclassification"
)

app = Flask(__name__)
app.secret_key="this is secret"

model = None


def _entropy(dist):
    """Entropy of class-distribution matrix"""
    p = dist / np.sum(dist, axis=0)
    pc = np.clip(p, 1e-15, 1)
    return np.sum(np.sum(- p * np.log2(pc), axis=0) *
                  np.sum(dist, axis=0) / np.sum(dist))


def _gini(dist):
    """Gini index of class-distribution matrix"""
    p = np.asarray(dist / np.sum(dist, axis=0))
    return np.sum((1 - np.sum(p ** 2, axis=0)) *
                  np.sum(dist, axis=0) / np.sum(dist))


@app.route("/",methods=["POST","GET"])
def dashboard():
    return render_template("index.html")

@app.route("/datamining", methods=["POST","GET"])
def datamining():
    if request.method=="POST":
        if request.form["action"]=="prosesdatamining":
            mydb.connect()
            cursor = mydb.cursor()
            cursor.execute("SELECT dataset.playerexperience, dataset.skill,dataset.intelligence,dataset.attitude, dataset.turnamen, dataset.target FROM dataset")
            rs = cursor.fetchall()
            cursor.close()
            mydb.close()

            df = pd.DataFrame(rs, columns=["experience","skill","intellegence","attitude","turnamen","Decision"])
            df["experience"] = df["experience"].str.lower()
            df["skill"] = df["skill"].str.lower()
            df["intellegence"] = df["intellegence"].str.lower()
            df["attitude"] = df["attitude"].str.lower()
            df["turnamen"] = df["turnamen"].str.lower()
            df["Decision"] = df["Decision"].str.lower()

            global_ = {}
            list_ = []

            for key in df:
                if key != "Decision":
                    k = Counter(df[key]).keys()
                    v = Counter(df[key]).values()
                    payload = {}
                    payload["name"]=key
                    for index, value in enumerate(k):
                        diterima = df[(df[key]==value) & (df["Decision"]=="diterima")]
                        tidakditerima = df[(df[key]==value) & (df["Decision"]=="tidak diterima")]
                        payload[value]=list(v)[index]
                        payload[value+"_diterima"] = len(diterima)
                        payload[value+"_tidakditerima"] = len(tidakditerima)
                        payload[value+"_entropy"] = _entropy([len(diterima),len(tidakditerima)])
                    jumlah =  payload["tidak"]+payload["lolos"]
                    diterima_ = payload["lolos_diterima"]+payload["tidak_diterima"]
                    tidakditerima_ = payload["tidak_tidakditerima"]+payload["lolos_tidakditerima"]
                    globalentropy = _entropy([diterima_,tidakditerima_])

                    global_["jumlah"] = jumlah
                    global_["diterima"] = diterima_
                    global_["tidakditerima"] = tidakditerima_
                    global_["entropy"] = globalentropy

                    gain1 = ((payload["lolos"]/jumlah)*payload["lolos_entropy"])+((payload["tidak"]/jumlah)*payload["tidak_entropy"])
                    gain2 = globalentropy-gain1

                    payload["gain"]=gain2

                list_.append(payload)
            list_.pop()
            return render_template("datamining.html",data=list_, global_=global_)
    return render_template("datamining.html");

@app.route("/logout")
def logout():
    session.pop("islogged")
    return redirect(url_for("login"))

@app.route("/login",methods=["GET","POST"])
def login():
    if 'islogged' in session:
        return redirect(url_for("dashboard"))
    if request.method=="POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if len(str(email))==0:
            return render_template("login.html",error="Masukkan data login...")
        elif len(str(password))==0:
            return render_template("login.html",error="Masukkan data login...")

        mydb.connect()
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM user WHERE email='{}'".format(email))
        fetch = cursor.fetchone()
        cursor.close()
        mydb.close()

        if fetch==None:
           return render_template("login.html",error="Login gagal...")
    
        if fetch[1]==email and fetch[2]==password:
            session["islogged"] = True
            return redirect(url_for("dashboard"))
        session["islogged"] = True
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/dataset",methods=["GET","POST"])
def index():
    if "islogged" not in session:
        return redirect(url_for("login"))
    if request.method=="POST":
        if request.files:
            dataset = request.files["dataset"]
            try:
                excel = pd.read_excel(dataset)
                tup = []

                count = -1

                for x in excel.iterrows():
                    count=count+1
                    tup.append((count,x[1]["Player Experience"],x[1]["Skill"],x[1]["Intellegence"],x[1]["Attitude"],x[1]["Turnamen"],x[1]["Target"]))

                mydb.connect()
                cursor = mydb.cursor()
                cursor.execute("DELETE FROM dataset")
                cursor.executemany("INSERT INTO dataset VALUES (%s,%s,%s,%s,%s,%s,%s)",tup)
                mydb.commit()
                cursor.close()
                mydb.close()

                return redirect(url_for("dashboard"))
            except Exception as e:
                return str(e)
        if request.form["hapusDatasetSingle"]=="true":
            i = request.form["id"]

            mydb.connect()
            cursor = mydb.cursor()
            cursor.execute("DELETE FROM dataset WHERE id=%s",(i,))
            mydb.commit()
            cursor.close()
            mydb.close()

            return redirect(url_for("dashboard"))

    mydb.connect()
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM dataset")
    rs = cursor.fetchall()
    cursor.close()
    mydb.close()

    obj = []
    for i,x in enumerate(rs):
        obj.append({
            "id":x[0],
            "no":i+1,
            "playerexperience":x[1],
            "skill":x[2],
            "intelligence":x[3],
            "attitude":x[4],
            "turnamen":x[5],
            "target":x[6]
        })

    return render_template("dashboard.html",data=json.dumps(obj))

@app.route("/generaterule", methods=["POST","GET"])
def generaterule():
    if "islogged" not in session:
        return redirect(url_for("login"))
    if request.method=="POST":

        mydb.connect()
        cursor = mydb.cursor()
        cursor.execute("SELECT dataset.playerexperience, dataset.skill,dataset.intelligence,dataset.attitude, dataset.turnamen, dataset.target FROM dataset")
        rs = cursor.fetchall()
        cursor.close()
        mydb.close()

        df = pd.DataFrame(rs, columns=["experience","skill","intellegence","attitude","turnamen","Decision"])
        df["experience"] = df["experience"].str.lower()
        df["skill"] = df["skill"].str.lower()
        df["intellegence"] = df["intellegence"].str.lower()
        df["attitude"] = df["attitude"].str.lower()
        df["turnamen"] = df["turnamen"].str.lower()
        df["Decision"] = df["Decision"].str.lower()


        config = {'algorithm': 'C4.5'}
        model = chef.fit(df, config = config)
        file = open("outputs/rules/rules.py","r")
        isi = file.read()

        return render_template("generaterule.html", isi=isi)
    return render_template("generaterule.html")

@app.route("/evaluasi", methods=["POST","GET"])
def evaluasi():
    if "islogged" not in session:
        return redirect(url_for("login"))
    if request.method=="POST":
        if request.files:
            dataset = request.files["dataset"]
            try:
                excel = pd.read_excel(dataset)
                tup = []

                count = -1

                for x in excel.iterrows():
                    count=count+1
                    tup.append((count,x[1]["Player Experience"],x[1]["Skill"],x[1]["Intellegence"],x[1]["Attitude"],x[1]["Turnamen"],x[1]["Target"]))

                mydb.connect()
                cursor = mydb.cursor()
                cursor.execute("DELETE FROM datasettesting")
                cursor.executemany("INSERT INTO datasettesting VALUES (%s,%s,%s,%s,%s,%s,%s)",tup)
                mydb.commit()
                cursor.close()
                mydb.close()

                return redirect(url_for("evaluasi"))
            except Exception as e:
                return str(e)
        if request.form["action"]=="hapusDatasettestingSingle":
                i = request.form["id"]

                mydb.connect()
                cursor = mydb.cursor()
                cursor.execute("DELETE FROM datasettesting WHERE id=%s",(i,))
                mydb.commit()
                cursor.close()
                mydb.close()

                return redirect(url_for("evaluasi"))
        if request.form["action"]=="ujidatatest":

            mydb.connect()
            cursor = mydb.cursor()
            cursor.execute("SELECT datasettesting.playerexperience, datasettesting.skill,datasettesting.intelligence,datasettesting.attitude, datasettesting.turnamen, datasettesting.target FROM datasettesting")
            rs = cursor.fetchall()
            cursor.close()
            mydb.close()

            df = pd.DataFrame(rs, columns=["experience","skill","intellegence","attitude","turnamen","Decision"])
            df["experience"] = df["experience"].str.lower()
            df["skill"] = df["skill"].str.lower()
            df["intellegence"] = df["intellegence"].str.lower()
            df["attitude"] = df["attitude"].str.lower()
            df["turnamen"] = df["turnamen"].str.lower()
            df["Decision"] = df["Decision"].str.lower()

            mydb.connect()
            cursor = mydb.cursor()
            cursor.execute("SELECT dataset.playerexperience, dataset.skill,dataset.intelligence,dataset.attitude, dataset.turnamen, dataset.target FROM dataset")
            rs2 = cursor.fetchall()
            cursor.close()
            mydb.close()

            df2 = pd.DataFrame(rs2, columns=["experience","skill","intellegence","attitude","turnamen","Decision"])
            df2["experience"] = df2["experience"].str.lower()
            df2["skill"] = df2["skill"].str.lower()
            df2["intellegence"] = df2["intellegence"].str.lower()
            df2["attitude"] = df2["attitude"].str.lower()
            df2["turnamen"] = df2["turnamen"].str.lower()
            df2["Decision"] = df2["Decision"].str.lower()

            config = {'algorithm': 'C4.5'}
            model = chef.fit(df2, config = config)

            benar = 0
            salah = 0

            payload = []
            
            for index,value in enumerate(df.iterrows()):
                predicted = chef.predict(model,df.iloc[index])
                actual = value[1]["Decision"]
                if predicted==actual:
                    benar=benar+1
                else:
                    salah=salah+1
                payload.append({
                    "no":index+1,
                    "playerexperience":value[1]["experience"],
                    "skill":value[1]["skill"],
                    "intellegence":value[1]["intellegence"],
                    "attitude":value[1]["attitude"],
                    "turnamen":value[1]["turnamen"],
                    "predicted":predicted,
                    "actual":actual
                })
            akurasi = (benar/(benar+salah))*100
            return render_template("evaluasi.html",data=json.dumps(payload), processed=True, akurasi=str(akurasi))
    mydb.connect()
    cursor = mydb.cursor()
    cursor.execute("SELECT datasettesting.id, datasettesting.playerexperience, datasettesting.skill,datasettesting.intelligence,datasettesting.attitude, datasettesting.turnamen, datasettesting.target FROM datasettesting")
    rs = cursor.fetchall()
    cursor.close()
    mydb.close()

    obj = []
    for i,x in enumerate(rs):
        obj.append({
            "id":x[0],
            "no":i+1,
            "playerexperience":x[1],
            "skill":x[2],
            "intelligence":x[3],
            "attitude":x[4],
            "turnamen":x[5],
            "target":x[6]
    })

    return render_template("evaluasi.html", data=json.dumps(obj))

@app.route("/prediksi", methods=["POST","GET"])
def prediksi():
    if "islogged" not in session:
        return redirect(url_for("login"))
    if request.method=="POST":
        try:
            playerexperience = request.form["playerexperience"]
            skill = request.form["skill"]
            intellegence = request.form["intellegence"]
            attitude = request.form["attitude"]
            turnamen = request.form["turnamen"]

            calonprediksi = pd.DataFrame([[playerexperience.lower(),skill.lower(),intellegence.lower(),attitude.lower(),turnamen.lower()]], columns=["experience","skill","intellegence","attitude","turnamen"])
            
            mydb.connect()
            cursor = mydb.cursor()
            cursor.execute("SELECT dataset.playerexperience, dataset.skill,dataset.intelligence,dataset.attitude, dataset.turnamen, dataset.target FROM dataset")
            rs = cursor.fetchall()
            cursor.close()
            mydb.close()

            df = pd.DataFrame(rs, columns=["experience","skill","intellegence","attitude","turnamen","Decision"])
            df["experience"] = df["experience"].str.lower()
            df["skill"] = df["skill"].str.lower()
            df["intellegence"] = df["intellegence"].str.lower()
            df["attitude"] = df["attitude"].str.lower()
            df["turnamen"] = df["turnamen"].str.lower()
            df["Decision"] = df["Decision"].str.lower()


            config = {'algorithm': 'C4.5'}
            model = chef.fit(df, config = config)

            result = chef.predict(model, calonprediksi.iloc[0])

            return render_template("prediksi.html",result=result)
        except Exception as e:
            return str(e)
    return render_template("prediksi.html")

if __name__=='__main__':
    app.run(debug=True)