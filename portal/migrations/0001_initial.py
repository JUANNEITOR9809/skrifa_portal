import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Lead",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=120)),
                ("negocio", models.CharField(max_length=120)),
                ("correo", models.EmailField(max_length=254)),
                ("necesidad", models.CharField(choices=[("inventario", "Inventario"), ("ventas", "Ventas y facturación"), ("citas", "Citas o reservas"), ("pedidos", "Pedidos a domicilio"), ("otro", "Otro")], max_length=20)),
                ("autoriza_datos", models.BooleanField(default=False)),
                ("acepta_publicidad", models.BooleanField(default=False)),
                ("creado", models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={"verbose_name": "solicitud de diagnóstico", "verbose_name_plural": "solicitudes de diagnóstico", "ordering": ["-creado"]},
        ),
        migrations.CreateModel(
            name="Cliente",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("empresa", models.CharField(max_length=120)),
                ("nit", models.CharField(blank=True, max_length=20)),
                ("representante", models.CharField(max_length=120)),
                ("cargo", models.CharField(blank=True, max_length=80)),
                ("celular", models.CharField(blank=True, max_length=20)),
                ("acepta_publicidad", models.BooleanField(default=False)),
                ("usuario", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="cliente", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Contrato",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("numero", models.CharField(max_length=20, unique=True)),
                ("objeto", models.CharField(max_length=200)),
                ("valor", models.PositiveIntegerField(help_text="Valor antes de IVA, en pesos")),
                ("plazo_semanas", models.PositiveSmallIntegerField(default=10)),
                ("firmado", models.BooleanField(default=False)),
                ("firmado_en", models.DateTimeField(blank=True, null=True)),
                ("ip_firma", models.CharField(blank=True, max_length=60)),
                ("huella", models.CharField(blank=True, max_length=64, verbose_name="huella SHA-256")),
                ("otp", models.CharField(blank=True, max_length=6)),
                ("otp_creado", models.DateTimeField(blank=True, null=True)),
                ("cliente", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="contratos", to="portal.cliente")),
            ],
        ),
        migrations.CreateModel(
            name="Pago",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("orden", models.PositiveSmallIntegerField()),
                ("concepto", models.CharField(max_length=60)),
                ("momento", models.CharField(max_length=80)),
                ("valor", models.PositiveIntegerField(help_text="Valor antes de IVA, en pesos")),
                ("estado", models.CharField(choices=[("bloqueado", "Aún no"), ("disponible", "Por pagar"), ("pagado", "Pagado")], default="bloqueado", max_length=12)),
                ("medio", models.CharField(blank=True, max_length=40)),
                ("factura", models.CharField(blank=True, max_length=20)),
                ("pagado_en", models.DateTimeField(blank=True, null=True)),
                ("contrato", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="pagos", to="portal.contrato")),
            ],
            options={"ordering": ["orden"]},
        ),
        migrations.CreateModel(
            name="Ticket",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tipo", models.CharField(choices=[("falla", "Falla en el programa"), ("peticion", "Petición"), ("queja", "Queja"), ("reclamo", "Reclamo"), ("consulta", "Consulta")], max_length=12)),
                ("descripcion", models.TextField()),
                ("correo", models.EmailField(max_length=254)),
                ("creado", models.DateTimeField(default=django.utils.timezone.now)),
                ("respondido", models.BooleanField(default=False)),
                ("respuesta", models.TextField(blank=True)),
                ("cliente", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="tickets", to="portal.cliente")),
            ],
            options={"verbose_name": "ticket de soporte (PQR)", "verbose_name_plural": "tickets de soporte (PQR)", "ordering": ["-creado"]},
        ),
        migrations.CreateModel(
            name="SolicitudDatos",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tipo", models.CharField(choices=[("consulta", "Consultar qué datos tienen de mí"), ("actualizar", "Actualizar o corregir mis datos"), ("suprimir", "Borrar mis datos y revocar la autorización")], max_length=12)),
                ("creado", models.DateTimeField(default=django.utils.timezone.now)),
                ("atendida", models.BooleanField(default=False)),
                ("cliente", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="solicitudes", to="portal.cliente")),
            ],
            options={"verbose_name": "solicitud de datos personales", "verbose_name_plural": "solicitudes de datos personales", "ordering": ["-creado"]},
        ),
    ]
