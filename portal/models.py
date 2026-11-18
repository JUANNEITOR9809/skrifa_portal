from django.conf import settings
from django.db import models
from django.utils import timezone

from .utils import sumar_dias_habiles


class Lead(models.Model):
    """Persona que pide el diagnóstico gratis desde la página de inicio."""
    NECESIDADES = [
        ("inventario", "Inventario"),
        ("ventas", "Ventas y facturación"),
        ("citas", "Citas o reservas"),
        ("pedidos", "Pedidos a domicilio"),
        ("otro", "Otro"),
    ]
    nombre = models.CharField(max_length=120)
    negocio = models.CharField(max_length=120)
    correo = models.EmailField()
    necesidad = models.CharField(max_length=20, choices=NECESIDADES)
    autoriza_datos = models.BooleanField(default=False)
    acepta_publicidad = models.BooleanField(default=False)
    creado = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "solicitud de diagnóstico"
        verbose_name_plural = "solicitudes de diagnóstico"
        ordering = ["-creado"]

    @property
    def radicado(self):
        return f"DG-{self.creado.year}-{self.pk:04d}"

    def __str__(self):
        return f"{self.radicado} · {self.negocio}"


class Cliente(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cliente")
    empresa = models.CharField(max_length=120)
    nit = models.CharField(max_length=20, blank=True)
    representante = models.CharField(max_length=120)
    cargo = models.CharField(max_length=80, blank=True)
    celular = models.CharField(max_length=20, blank=True)
    acepta_publicidad = models.BooleanField(default=False)

    def __str__(self):
        return self.empresa


class Contrato(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="contratos")
    numero = models.CharField(max_length=20, unique=True)
    objeto = models.CharField(max_length=200)
    valor = models.PositiveIntegerField(help_text="Valor antes de IVA, en pesos")
    plazo_semanas = models.PositiveSmallIntegerField(default=10)
    firmado = models.BooleanField(default=False)
    firmado_en = models.DateTimeField(null=True, blank=True)
    ip_firma = models.CharField(max_length=60, blank=True)
    huella = models.CharField("huella SHA-256", max_length=64, blank=True)
    otp = models.CharField(max_length=6, blank=True)
    otp_creado = models.DateTimeField(null=True, blank=True)

    def texto_para_firmar(self):
        return (f"CONTRATO {self.numero}|SKRIFA LABS S.A.S.|{self.cliente.empresa}|"
                f"{self.objeto}|{self.valor}|{self.plazo_semanas} semanas")

    def __str__(self):
        return self.numero


class Pago(models.Model):
    BLOQUEADO, DISPONIBLE, PAGADO = "bloqueado", "disponible", "pagado"
    ESTADOS = [(BLOQUEADO, "Aún no"), (DISPONIBLE, "Por pagar"), (PAGADO, "Pagado")]
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name="pagos")
    orden = models.PositiveSmallIntegerField()
    concepto = models.CharField(max_length=60)
    momento = models.CharField(max_length=80)
    valor = models.PositiveIntegerField(help_text="Valor antes de IVA, en pesos")
    estado = models.CharField(max_length=12, choices=ESTADOS, default=BLOQUEADO)
    medio = models.CharField(max_length=40, blank=True)
    factura = models.CharField(max_length=20, blank=True)
    pagado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["orden"]

    @property
    def iva(self):
        return round(self.valor * 0.19)

    @property
    def total(self):
        return self.valor + self.iva

    def __str__(self):
        return f"{self.contrato.numero} · {self.concepto}"


class Ticket(models.Model):
    TIPOS = [
        ("falla", "Falla en el programa"),
        ("peticion", "Petición"),
        ("queja", "Queja"),
        ("reclamo", "Reclamo"),
        ("consulta", "Consulta"),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="tickets")
    tipo = models.CharField(max_length=12, choices=TIPOS)
    descripcion = models.TextField()
    correo = models.EmailField()
    creado = models.DateTimeField(default=timezone.now)
    respondido = models.BooleanField(default=False)
    respuesta = models.TextField(blank=True)

    class Meta:
        verbose_name = "ticket de soporte (PQR)"
        verbose_name_plural = "tickets de soporte (PQR)"
        ordering = ["-creado"]

    @property
    def radicado(self):
        return f"PQR-{self.creado.year}-{self.pk:04d}"

    @property
    def fecha_limite(self):
        return sumar_dias_habiles(timezone.localtime(self.creado).date(), 15)

    def __str__(self):
        return self.radicado


class SolicitudDatos(models.Model):
    """Ejercicio de los derechos de habeas data (Ley 1581 de 2012)."""
    TIPOS = [
        ("consulta", "Consultar qué datos tienen de mí"),
        ("actualizar", "Actualizar o corregir mis datos"),
        ("suprimir", "Borrar mis datos y revocar la autorización"),
    ]
    PLAZOS = {"consulta": 10, "actualizar": 15, "suprimir": 15}
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="solicitudes")
    tipo = models.CharField(max_length=12, choices=TIPOS)
    creado = models.DateTimeField(default=timezone.now)
    atendida = models.BooleanField(default=False)

    class Meta:
        verbose_name = "solicitud de datos personales"
        verbose_name_plural = "solicitudes de datos personales"
        ordering = ["-creado"]

    @property
    def fecha_limite(self):
        return sumar_dias_habiles(timezone.localtime(self.creado).date(), self.PLAZOS[self.tipo])

    def __str__(self):
        return f"{self.get_tipo_display()} · {self.cliente}"
