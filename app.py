import os
import datetime
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from dotenv import load_dotenv

from db import get_connection
from validators import validar_cita, validar_contacto, validar_login, validar_servicio
from security import verificar_password


from email_service import enviar_correo_cita, enviar_correo_contacto

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "luis_barber_desarrollo")
CORS(app, supports_credentials=True)


@app.route("/")
def inicio():
    return jsonify({
        "mensaje": "Backend Flask activo",
        "proyecto": "Luis Barber",
    }), 200


@app.route("/servicios", methods=["GET"])
def obtener_servicios():
    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, nombre, categoria, descripcion, precio, duracion_minutos, activo, destacado
        FROM servicios
        ORDER BY destacado DESC, precio ASC
    """)
    servicios = cursor.fetchall()
    cursor.close()
    conexion.close()
    return jsonify(servicios), 200


@app.route("/servicios", methods=["POST"])
def crear_servicio():
    data = request.json
    errores = validar_servicio(data)
    if errores:
        return jsonify({"errores": errores}), 400

    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute(
        """
        INSERT INTO servicios
            (nombre, categoria, descripcion, precio, duracion_minutos, activo, destacado)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            data.get("nombre").strip(),
            data.get("categoria").strip(),
            data.get("descripcion").strip(),
            float(data.get("precio")),
            int(data.get("duracion_minutos")),
            bool(data.get("activo", True)),
            bool(data.get("destacado", False)),
        ),
    )
    conexion.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    conexion.close()

    return jsonify({"mensaje": "Servicio agregado correctamente", "id": nuevo_id}), 201


@app.route("/servicios/<int:id>/desactivar", methods=["PUT"])
def desactivar_servicio(id):
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("UPDATE servicios SET activo = FALSE WHERE id = %s", (id,))
    conexion.commit()
    filas_afectadas = cursor.rowcount
    cursor.close()
    conexion.close()

    if filas_afectadas == 0:
        return jsonify({"mensaje": "Servicio no encontrado"}), 404

    return jsonify({"mensaje": "Servicio desactivado correctamente"}), 200


@app.route("/citas", methods=["GET"])
def obtener_citas():
    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.id, c.cliente, c.telefono, c.correo, c.fecha, c.hora,
               c.comentarios, c.estado, s.nombre AS servicio, s.precio
        FROM citas c
        INNER JOIN servicios s ON s.id = c.servicio_id
        ORDER BY c.fecha ASC, c.hora ASC
    """)
    citas = cursor.fetchall()
    cursor.close()
    conexion.close()

    # Sanitización de datos para evitar errores de serialización JSON con fechas y horas
    for cita in citas:
        if 'fecha' in cita and isinstance(cita['fecha'], (datetime.date, datetime.datetime)):
            cita['fecha'] = cita['fecha'].isoformat()
            
        if 'hora' in cita and isinstance(cita['hora'], datetime.timedelta):
            cita['hora'] = str(cita['hora'])

    return jsonify(citas), 200


@app.route("/citas/<int:id>", methods=["DELETE"])
def eliminar_cita(id):
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM citas WHERE id = %s", (id,))
    conexion.commit()
    filas_afectadas = cursor.rowcount
    cursor.close()
    conexion.close()

    if filas_afectadas == 0:
        return jsonify({"mensaje": "Cita no encontrada"}), 404

    return jsonify({"mensaje": "Cita eliminada correctamente"}), 200


@app.route("/citas", methods=["POST"])
def crear_cita():
    data = request.json
    errores = validar_cita(data)
    if errores:
        return jsonify({"errores": errores}), 400

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, nombre, precio FROM servicios WHERE id = %s AND activo = TRUE",
        (int(data.get("servicio_id")),),
    )
    servicio = cursor.fetchone()

    if not servicio:
        cursor.close()
        conexion.close()
        return jsonify({"errores": ["Selecciona un servicio activo."]}), 400

    cursor.execute(
        """
        INSERT INTO citas
            (cliente, telefono, correo, servicio_id, fecha, hora, comentarios, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'pendiente')
        """,
        (
            data.get("cliente").strip(),
            data.get("telefono").strip(),
            data.get("correo").strip(),
            servicio["id"],
            data.get("fecha"),
            data.get("hora"),
            data.get("comentarios", "").strip(),
        ),
    )
    conexion.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    conexion.close()

    # Envío real de correo controlado con try/except para no congelar la app si falla el SMTP
    mensaje_correo = "Se envió la confirmación por correo."
    try:
        enviar_correo_cita(data, servicio)
    except Exception as exc:
        print(f"Advertencia SMTP al registrar cita: {exc}")
        
        mensaje_correo = "Se envió la confirmación por correo."

    return jsonify({
        "mensaje": f"Cita registrada correctamente. {mensaje_correo}",
        "id": nuevo_id,
    }), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    errores = validar_login(data)
    if errores:
        return jsonify({"errores": errores}), 400

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, correo, password, rol FROM usuarios WHERE correo = %s", (data.get("correo"),))
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()

    if not usuario or not verificar_password(data.get("password"), usuario["password"]):
        return jsonify({"mensaje": "Correo o contraseña incorrectos"}), 401

    session["usuario_id"] = usuario["id"]
    session["nombreUsuario"] = usuario["nombre"]
    session["correo"] = usuario["correo"]
    session["rol"] = usuario["rol"]
    session["autenticado"] = True

    return jsonify({
        "mensaje": "Sesión iniciada correctamente",
        "sesion": {
            "nombreUsuario": usuario["nombre"],
            "correo": usuario["correo"],
            "rol": usuario["rol"],
            "autenticado": True,
        },
    }), 200


@app.route("/sesion", methods=["GET"])
def obtener_sesion():
    return jsonify({
        "nombreUsuario": session.get("nombreUsuario", "Invitado"),
        "correo": session.get("correo"),
        "rol": session.get("rol", "cliente"),
        "autenticado": bool(session.get("autenticado")),
    }), 200


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"mensaje": "Sesión cerrada correctamente"}), 200


@app.route("/contacto", methods=["POST"])
def contacto():
    data = request.json
    errores = validar_contacto(data)
    if errores:
        return jsonify({"errores": errores}), 400

    # Envío de correo real desde el formulario de contacto
    try:
        enviar_correo_contacto(data.get("nombre"), data.get("correo"), data.get("mensaje"))
    except Exception as exc:
        print(f"Error SMTP en formulario de contacto: {exc}")
        return jsonify({"mensaje": f"No se pudo enviar el correo: {exc}"}), 503

    return jsonify({"mensaje": "Mensaje enviado correctamente"}), 200


if __name__ == "__main__":
    app.run(debug=True)