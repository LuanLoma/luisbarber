from werkzeug.security import generate_password_hash, check_password_hash


def generar_hash(password):
    """Genera un hash seguro para guardar contraseñas."""
    return generate_password_hash(password)


def verificar_password(password_plano, password_hash):
    """Compara la contraseña escrita con el hash almacenado."""
    return check_password_hash(password_hash, password_plano)
