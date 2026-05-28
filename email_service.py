import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# --- FUERZA LA RUTA ABSOLUTA DEL ARCHIVO .ENV ---
base_dir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(base_dir, '.env')

# Si el .env está en la carpeta padre (raíz del backend), subimos un nivel:
if not os.path.exists(env_path):
    env_path = os.path.join(base_dir, '..', '.env')

load_dotenv(dotenv_path=env_path)
# ------------------------------------------------


def _enviar(subject, contenido, destinatario=None):
    user = os.getenv("MAIL_USER")
    password = os.getenv("MAIL_PASSWORD")
    server = os.getenv("MAIL_SERVER")
    port = os.getenv("MAIL_PORT", "587")

    # Validación de control para ver en consola si fallan las variables
    if not user or not password:
        raise Exception(
            f"Error crítico: No se pudieron cargar las credenciales desde el archivo .env. "
            f"Ruta buscada: {os.path.abspath(env_path)}"
        )

    email = EmailMessage()
    email["Subject"] = subject
    email["From"] = user
    
    # MODIFICACIÓN: Si es una lista o tupla, los une separados por comas para enviar a múltiples buzones
    if isinstance(destinatario, (list, tuple)):
        email["To"] = ", ".join(destinatario)
    else:
        email["To"] = destinatario or os.getenv("MAIL_TO", user)
        
    email.set_content(contenido)

    with smtplib.SMTP(server, int(port)) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(email)


def enviar_correo_contacto(nombre, correo, mensaje):
    _enviar(
        "Nuevo mensaje para Luis Barber",
        f"""Nuevo mensaje recibido desde el formulario de contacto.

Nombre: {nombre}
Correo: {correo}

Mensaje:
{mensaje}
""",
    )


def enviar_correo_cita(data, servicio):
    contenido = f"""Cita registrada en Luis Barber.

Cliente: {data.get("cliente")}
Telefono: {data.get("telefono")}
Correo: {data.get("correo")}
Servicio: {servicio.get("nombre")}
Precio: ${servicio.get("precio")}
Fecha: {data.get("fecha")}
Hora: {data.get("hora")}

Comentarios:
{data.get("comentarios", "Sin comentarios")}
"""
    # Recuperamos tu correo de administrador configurado en el .env
    correo_barbero = os.getenv("MAIL_TO") or os.getenv("MAIL_USER")
    correo_cliente = data.get("correo")
    
    # Creamos una lista con ambos correos para que se envíe en conjunto
    destinatarios = [correo_cliente, correo_barbero]
    
    # Se invoca la función pasando la lista unificada
    _enviar("Confirmacion de cita - Luis Barber", contenido, destinatarios)