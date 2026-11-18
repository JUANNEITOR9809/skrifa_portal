from datetime import timedelta


def sumar_dias_habiles(fecha, dias):
    """Suma días hábiles (lunes a viernes). No descuenta festivos."""
    resultado = fecha
    contados = 0
    while contados < dias:
        resultado += timedelta(days=1)
        if resultado.weekday() < 5:
            contados += 1
    return resultado


def ip_del_cliente(request):
    """IP real del usuario. En Render llega en la cabecera X-Forwarded-For."""
    reenviada = request.META.get("HTTP_X_FORWARDED_FOR")
    if reenviada:
        return reenviada.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def pesos(valor):
    return "$" + f"{int(valor):,}".replace(",", ".")
