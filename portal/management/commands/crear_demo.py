from django.core.management.base import BaseCommand

from portal.demo import DEMO_CLAVE, DEMO_USUARIO, crear_o_reiniciar_demo


class Command(BaseCommand):
    help = "Crea el cliente de ejemplo (Ferretería El Tornillo) para la demostración."

    def handle(self, *args, **options):
        crear_o_reiniciar_demo()
        self.stdout.write(self.style.SUCCESS(f"Cliente de ejemplo listo. Usuario: {DEMO_USUARIO} · Contraseña: {DEMO_CLAVE}"))
