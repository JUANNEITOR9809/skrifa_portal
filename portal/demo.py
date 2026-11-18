from django.contrib.auth import get_user_model
from datetime import timedelta

from django.utils import timezone

from .models import Cliente, Contrato, Pago, Ticket

DEMO_USUARIO = "gerencia@ferreteriaeltornillo.co"
DEMO_CLAVE = "Tornillo2026"


def crear_o_reiniciar_demo():
    """Crea (o deja como nuevo) el cliente de ejemplo Ferretería El Tornillo."""
    User = get_user_model()
    user, _ = User.objects.get_or_create(username=DEMO_USUARIO, defaults={"email": DEMO_USUARIO, "first_name": "Carlos Andrés", "last_name": "Pineda"})
    user.set_password(DEMO_CLAVE)
    user.save()
    cliente, _ = Cliente.objects.update_or_create(
        usuario=user,
        defaults={"empresa": "Ferretería El Tornillo S.A.S.", "nit": "901.234.567-8", "representante": "Carlos Andrés Pineda",
                  "cargo": "Gerente", "celular": "310 555 0142", "acepta_publicidad": False},
    )
    cliente.contratos.all().delete()
    cliente.tickets.all().delete()
    cliente.solicitudes.all().delete()
    contrato = Contrato.objects.create(cliente=cliente, numero="SL-2026-0001",
                                       objeto="Desarrollo de un sistema web de inventario y ventas a la medida",
                                       valor=12_000_000, plazo_semanas=10)
    Pago.objects.bulk_create([
        Pago(contrato=contrato, orden=1, concepto="Anticipo (40 %)", momento="Al aceptar el contrato", valor=4_800_000),
        Pago(contrato=contrato, orden=2, concepto="Versión Beta (40 %)", momento="Al entregar la versión de pruebas", valor=4_800_000),
        Pago(contrato=contrato, orden=3, concepto="Entrega final (20 %)", momento="Con el acta de aceptación final", valor=2_400_000),
    ])
    Ticket.objects.create(cliente=cliente, tipo="consulta", correo=DEMO_USUARIO,
                          descripcion="¿Cuántos usuarios puede tener el sistema de inventario?",
                          creado=timezone.now() - timedelta(days=6), respondido=True,
                          respuesta="El sistema no tiene límite de usuarios.")
    return cliente
