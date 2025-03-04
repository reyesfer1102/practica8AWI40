# python.exe -m venv .venv
# cd .venv/Scripts
# activate.bat
# py -m ensurepip --upgrade
# pip install -r requirements.txt

from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify, make_response

import mysql.connector

import datetime
import pytz

from flask_cors import CORS, cross_origin

# Función para obtener una nueva conexión a la base de datos en cada petición
def get_connection():
    return mysql.connector.connect(
        host="82.197.82.90",
        database="u861594054_practica8",
        user="u861594054_villa",
        password="]ztsup5W"
    )

app = Flask(__name__)
CORS(app)

# Página de inicio
@app.route("/")
def index():
    return render_template("index.html")


##################################
# Endpoints para la tabla empleados
##################################

# Listar empleados
@app.route("/empleados")
def listar_empleados():
    con = get_connection()
    cursor = con.cursor(dictionary=True)
    sql = "SELECT idEmpleado, nombreEmpleado, numero, fechaIngreso FROM empleados LIMIT 10 OFFSET 0"
    cursor.execute(sql)
    empleados = cursor.fetchall()
    con.close()
    return render_template("empleados.html", empleados=empleados)

# Buscar empleados (por id, nombre, número o fechaIngreso)
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
        LIMIT 10 OFFSET 0
    """
    val = (busqueda_pattern, busqueda_pattern, busqueda_pattern, busqueda_pattern)
    try:
        cursor.execute(sql, val)
        registros = cursor.fetchall()
    except mysql.connector.Error as error:
        print(f"Error en la consulta de empleados: {error}")
        registros = []
    finally:
        con.close()
    return make_response(jsonify(registros))

# Guardar (insertar o actualizar) un empleado
@app.route("/empleado", methods=["POST"])
@cross_origin()
def guardar_empleado():
    # Se espera que el formulario contenga:
    # - idEmpleado (opcional, para actualizar)
    # - nombreEmpleado
    # - numero
    # - fechaIngreso (formato YYYY-MM-DD)
    idEmpleado = request.form.get("idEmpleado", None)
    nombreEmpleado = request.form["nombreEmpleado"]
    numero = request.form["numero"]
    fechaIngreso = request.form["fechaIngreso"]

    con = get_connection()
    cursor = con.cursor()
    if idEmpleado:
        # Actualización de empleado
        sql = """
            UPDATE empleados
            SET nombreEmpleado = %s,
                numero = %s,
                fechaIngreso = %s
            WHERE idEmpleado = %s
        """
        val = (nombreEmpleado, numero, fechaIngreso, idEmpleado)
    else:
        # Inserción de nuevo empleado
        sql = """
            INSERT INTO empleados (nombreEmpleado, numero, fechaIngreso)
            VALUES (%s, %s, %s)
        """
        val = (nombreEmpleado, numero, fechaIngreso)
    cursor.execute(sql, val)
    con.commit()
    con.close()
    return make_response(jsonify({}))

# Obtener datos de un empleado para edición
@app.route("/empleado/<int:idEmpleado>")
def editar_empleado(idEmpleado):
    con = get_connection()
    cursor = con.cursor(dictionary=True)
    sql = "SELECT idEmpleado, nombreEmpleado, numero, fechaIngreso FROM empleados WHERE idEmpleado = %s"
    val = (idEmpleado,)
    cursor.execute(sql, val)
    registro = cursor.fetchone()
    con.close()
    return make_response(jsonify(registro))

# Eliminar un empleado
@app.route("/empleado/eliminar", methods=["POST"])
def eliminar_empleado():
    idEmpleado = request.form["idEmpleado"]
    con = get_connection()
    cursor = con.cursor()
    sql = "DELETE FROM empleados WHERE idEmpleado = %s"
    val = (idEmpleado,)
    cursor.execute(sql, val)
    con.commit()
    con.close()
    return make_response(jsonify({}))


##################################
# Endpoints para la tabla reportes
##################################

# Listar reportes
@app.route("/reportes")
def listar_reportes():
    con = get_connection()
    cursor = con.cursor(dictionary=True)
    sql = """
        SELECT idReporte, idEmpleado, descripcion, area, fechaHora, estado
        FROM reportes
        LIMIT 10 OFFSET 0
    """
    cursor.execute(sql, )
    reportes = cursor.fetchall()
    con.close()
    return render_template("reportes.html", reportes=reportes)

# Buscar reportes (por idReporte, descripción, área o estado)
@app.route("/reportes/buscar", methods=["GET"])
def buscar_reportes():
    busqueda = request.args.get("busqueda", "")
    busqueda_pattern = f"%{busqueda}%"
    con = get_connection()
    cursor = con.cursor(dictionary=True)
    sql = """
        SELECT idReporte, idEmpleado, descripcion, area, fechaHora, estado
        FROM reportes
        WHERE CAST(idReporte AS CHAR) LIKE %s
           OR descripcion LIKE %s
           OR area LIKE %s
           OR estado LIKE %s
        ORDER BY idReporte DESC
        LIMIT 10 OFFSET 0
    """
    val = (busqueda_pattern, busqueda_pattern, busqueda_pattern, busqueda_pattern)
    try:
        cursor.execute(sql, val)
        registros = cursor.fetchall()
    except mysql.connector.Error as error:
        print(f"Error en la consulta de reportes: {error}")
        registros = []
    finally:
        con.close()
    return make_response(jsonify(registros))

# Guardar (insertar o actualizar) un reporte
@app.route("/reporte", methods=["POST"])
@cross_origin()
def guardar_reporte():
    # Se espera:
    # - idReporte (opcional para actualizar)
    # - idEmpleado
    # - descripcion
    # - area
    # - fechaHora (opcional: se usa la hora actual en UTC si no se envía)
    # - estado (opcional, por defecto "Sin Revision")
    idReporte = request.form.get("idReporte", None)
    idEmpleado = request.form["idEmpleado"]
    descripcion = request.form["descripcion"]
    area = request.form["area"]
    fechaHora = request.form.get(
        "fechaHora",
        datetime.datetime.now(pytz.timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S")
    )
    estado = request.form.get("estado", "Sin Revision")

    con = get_connection()
    cursor = con.cursor()
    if idReporte:
        sql = """
            UPDATE reportes
            SET idEmpleado = %s,
                descripcion = %s,
                area = %s,
                fechaHora = %s,
                estado = %s
            WHERE idReporte = %s
        """
        val = (idEmpleado, descripcion, area, fechaHora, estado, idReporte)
    else:
        sql = """
            INSERT INTO reportes (idEmpleado, descripcion, area, fechaHora, estado)
            VALUES (%s, %s, %s, %s, %s)
        """
        val = (idEmpleado, descripcion, area, fechaHora, estado)
    cursor.execute(sql, val)
    con.commit()
    con.close()
    return make_response(jsonify({}))

# Obtener datos de un reporte para edición
@app.route("/reporte/<int:idReporte>")
def editar_reporte(idReporte):
    con = get_connection()
    cursor = con.cursor(dictionary=True)
    sql = "SELECT idReporte, idEmpleado, descripcion, area, fechaHora, estado FROM reportes WHERE idReporte = %s"
    val = (idReporte,)
    cursor.execute(sql, val)
    registro = cursor.fetchone()
    con.close()
    return make_response(jsonify(registro))

# Eliminar un reporte
@app.route("/reporte/eliminar", methods=["POST"])
def eliminar_reporte():
    idReporte = request.form["idReporte"]
    con = get_connection()
    cursor = con.cursor()
    sql = "DELETE FROM reportes WHERE idReporte = %s"
    val = (idReporte,)
    cursor.execute(sql, val)
    con.commit()
    con.close()
    return make_response(jsonify({}))


##################################
# Endpoint para listar reporteslog
##################################
@app.route("/reporteslog")
def listar_reporteslog():
    con = get_connection()
    cursor = con.cursor(dictionary=True)
    sql = """
        SELECT idLog, idReporte, estado, fechaHora
        FROM reporteslog
        LIMIT 10 OFFSET 0
    """
    cursor.execute(sql)
    logs = cursor.fetchall()
    con.close()
    return render_template("reporteslog.html", reporteslog=logs)


if _name_ == "_main_":
    app.run(debug=True)
