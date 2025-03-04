from flask import Flask, render_template, request, jsonify, make_response
import mysql.connector
import datetime
import pytz
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración de la base de datos
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_DATABASE"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

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

@app.route("/empleados/buscar", methods=["GET"])
def buscar_empleados():
    busqueda = request.args.get("busqueda", "")
    busqueda_pattern = f"%{busqueda}%"
    con = get_connection()
    cursor = con.cursor(dictionary=True)
    sql = """
        SELECT idEmpleado, nombreEmpleado, numero, fechaIngreso 
        FROM empleados
        WHERE CAST(idEmpleado AS CHAR) LIKE %s
           OR nombreEmpleado LIKE %s
           OR CAST(numero AS CHAR) LIKE %s
           OR CAST(fechaIngreso AS CHAR) LIKE %s
        ORDER BY idEmpleado DESC
        LIMIT 10
    """
    val = (busqueda_pattern, busqueda_pattern, busqueda_pattern, busqueda_pattern)
    cursor.execute(sql, val)
    registros = cursor.fetchall()
    con.close()
    return make_response(jsonify(registros))

@app.route("/empleado", methods=["POST"])
def guardar_empleado():
    idEmpleado = request.form.get("idEmpleado", None)
    nombreEmpleado = request.form["nombreEmpleado"]
    numero = request.form["numero"]
    fechaIngreso = request.form["fechaIngreso"]

    con = get_connection()
    cursor = con.cursor()
    if idEmpleado:
        sql = """
            UPDATE empleados SET nombreEmpleado = %s, numero = %s, fechaIngreso = %s WHERE idEmpleado = %s
        """
        val = (nombreEmpleado, numero, fechaIngreso, idEmpleado)
    else:
        sql = """
            INSERT INTO empleados (nombreEmpleado, numero, fechaIngreso) VALUES (%s, %s, %s)
        """
        val = (nombreEmpleado, numero, fechaIngreso)
    cursor.execute(sql, val)
    con.commit()
    con.close()
    return make_response(jsonify({}))

@app.route("/empleado/<int:idEmpleado>")
def editar_empleado(idEmpleado):
    con = get_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT idEmpleado, nombreEmpleado, numero, fechaIngreso FROM empleados WHERE idEmpleado = %s", (idEmpleado,))
    registro = cursor.fetchone()
    con.close()
    return make_response(jsonify(registro))

@app.route("/empleado/eliminar", methods=["POST"])
def eliminar_empleado():
    idEmpleado = request.form["idEmpleado"]
    con = get_connection()
    cursor = con.cursor()
    cursor.execute("DELETE FROM empleados WHERE idEmpleado = %s", (idEmpleado,))
    con.commit()
    con.close()
    return make_response(jsonify({}))
