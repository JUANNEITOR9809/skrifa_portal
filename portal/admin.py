from django.contrib import admin

from .models import Cliente, Contrato, Lead, Pago, SolicitudDatos, Ticket


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("radicado", "nombre", "negocio", "correo", "necesidad", "autoriza_datos", "acepta_publicidad", "creado")
    list_filter = ("necesidad", "acepta_publicidad")


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("empresa", "representante", "usuario", "acepta_publicidad")


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 0


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ("numero", "cliente", "valor", "firmado", "firmado_en", "ip_firma")
    readonly_fields = ("huella", "firmado_en", "ip_firma")
    inlines = [PagoInline]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("radicado", "cliente", "tipo", "creado", "fecha_limite", "respondido")
    list_filter = ("tipo", "respondido")


@admin.register(SolicitudDatos)
class SolicitudDatosAdmin(admin.ModelAdmin):
    list_display = ("cliente", "tipo", "creado", "fecha_limite", "atendida")
