from db import get_connection
from security import generar_hash


def crear_usuario(nombre, correo, password):
    conexion = get_connection()
    cursor = conexion.cursor()

    password_hash = generar_hash(password)

    cursor.execute(
        "INSERT INTO usuarios (nombre, correo, password, rol) VALUES (%s, %s, %s, %s)",
        (nombre, correo, password_hash, "admin")
    )

    conexion.commit()
    cursor.close()
    conexion.close()
    print("Usuario creado correctamente")


if __name__ == "__main__":
    crear_usuario("Luis Administrador", "admin@luisbarber.com", "12345")
