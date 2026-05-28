def validar_servicio(data):
    errores = []
    if not data:
        return ["No se recibieron datos."]

    if not str(data.get("nombre", "")).strip():
        errores.append("El nombre del servicio es obligatorio.")
    if not str(data.get("categoria", "")).strip():
        errores.append("La categoría es obligatoria.")
    if not str(data.get("descripcion", "")).strip():
        errores.append("La descripción es obligatoria.")

    try:
        precio = float(data.get("precio", 0))
        if precio <= 0:
            errores.append("El precio debe ser mayor que 0.")
    except (TypeError, ValueError):
        errores.append("El precio debe ser un número válido.")

    try:
        duracion = int(data.get("duracion_minutos", 0))
        if duracion < 15:
            errores.append("La duración debe ser de al menos 15 minutos.")
    except (TypeError, ValueError):
        errores.append("La duración debe ser un número entero.")

    return errores


def validar_cita(data):
    errores = []
    if not data:
        return ["No se recibieron datos."]

    campos = {
        "cliente": "El nombre del cliente es obligatorio.",
        "telefono": "El teléfono es obligatorio.",
        "correo": "El correo es obligatorio.",
        "servicio_id": "Selecciona un servicio.",
        "fecha": "La fecha es obligatoria.",
        "hora": "La hora es obligatoria.",
    }

    for campo, mensaje in campos.items():
        if not str(data.get(campo, "")).strip():
            errores.append(mensaje)

    if data.get("correo") and "@" not in data.get("correo"):
        errores.append("El correo debe tener un formato válido.")

    try:
        if data.get("servicio_id"):
            int(data.get("servicio_id"))
    except (TypeError, ValueError):
        errores.append("El servicio seleccionado no es válido.")

    return errores


def validar_login(data):
    errores = []
    if not data:
        return ["No se recibieron datos."]
    if not str(data.get("correo", "")).strip():
        errores.append("El correo es obligatorio.")
    if not str(data.get("password", "")).strip():
        errores.append("La contraseña es obligatoria.")
    return errores


def validar_contacto(data):
    errores = []
    if not data:
        return ["No se recibieron datos."]
    if not str(data.get("nombre", "")).strip():
        errores.append("El nombre es obligatorio.")
    if not str(data.get("correo", "")).strip():
        errores.append("El correo es obligatorio.")
    if data.get("correo") and "@" not in data.get("correo"):
        errores.append("El correo debe tener un formato válido.")
    if not str(data.get("mensaje", "")).strip():
        errores.append("El mensaje es obligatorio.")
    return errores
