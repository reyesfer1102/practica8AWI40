from flask import Flask

from flask import render_template
from flask import request
from flask import jsonify, make_response

import mysql.connector

import datetime
import pytz

from flask_cors import CORS, cross_origin

con = mysql.connector.connect(
    host="82.197.82.90",
    database="u861594054_practica8",
    user="u861594054_villa",
    password="/iJRzrJBz+P1"
)
app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/empleados")
def listar_empleados():
    con = get_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT idEmpleado, nombreEmpleado, numero, fechaIngreso FROM empleados LIMIT 10")
    empleados = cursor.fetchall()
    con.close()
    return render_template("empleados.html", empleados=empleados)

@app.route("/reportes")
def reportes():
    con = get_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT idEmpleado, nombreEmpleado, numero, fechaIngreso FROM empleados LIMIT 10")
    reportes = cursor.fetchall()
    con.close()
    return render_template("reportes.html", reportes=reportes)
