from flask import Flask, render_template, request, redirect, url_for,session
import pandas as pd 
import json
import mysql.connector
from chefboost import Chefboost as chef
from sklearn.model_selection import train_test_split

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="esportclassification"
)

app = Flask(__name__)
app.secret_key="this is secret"

model = None

@app.route("/logout")
def logout():
    session.pop("islogged")
    return redirect(url_for("login"))

@app.route("/login",methods=["GET","POST"])
def login():
    if 'islogged' in session:
        return redirect(url_for("index"))
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
            return redirect(url_for("index"))
        session["islogged"] = True
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/",methods=["GET","POST"])
def index():
    if "islogged" not in session:
        return redirect(url_for("login"))
    if request.method=="POST" and request.files:
        dataset = request.files["dataset"]
        try:
            excel = pd.read_excel(dataset)
            tup = []

            for x in excel.iterrows():
                tup.append((x[1]["Player Experience"],x[1]["Skill"],x[1]["Intellegence"],x[1]["Attitude"],x[1]["Turnamen"],x[1]["Target"]))

            mydb.connect()
            cursor = mydb.cursor()
            cursor.execute("DELETE FROM dataset")
            cursor.executemany("INSERT INTO dataset VALUES (%s,%s,%s,%s,%s,%s)",tup)
            mydb.commit()
            cursor.close()
            mydb.close()

            return redirect(url_for("index"))
        except Exception as e:
            return str(e)

    mydb.connect()
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM dataset")
    rs = cursor.fetchall()
    cursor.close()
    mydb.close()

    obj = []
    for i,x in enumerate(rs):
        obj.append({
            "no":i+1,
            "playerexperience":x[0],
            "skill":x[1],
            "intelligence":x[2],
            "attitude":x[3],
            "turnamen":x[4],
            "target":x[5]
        })

    return render_template("dashboard.html",data=json.dumps(obj))

@app.route("/generaterule", methods=["POST","GET"])
def generaterule():
    if "islogged" not in session:
        return redirect(url_for("login"))
    if request.method=="POST":

        mydb.connect()
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM dataset")
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

@app.route("/evaluasi")
def evaluasi():
    if "islogged" not in session:
        return redirect(url_for("login"))
    mydb.connect()
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM dataset")
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
    train, test = train_test_split(df, test_size=0.2, random_state=0)
    
    config = {'algorithm': 'C4.5'}
    model = chef.fit(train, config = config)

    benar = 0
    salah = 0

    payload = []
    
    for index,value in enumerate(test.iterrows()):
        predicted = chef.predict(model,test.iloc[index])
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
    return render_template("evaluasi.html",akurasi=akurasi,data=json.dumps(payload))

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
            cursor.execute("SELECT * FROM dataset")
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