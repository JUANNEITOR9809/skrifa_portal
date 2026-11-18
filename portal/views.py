import hashlib
from datetime import timedelta
import secrets

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .demo import DEMO_CLAVE, DEMO_USUARIO, crear_o_reiniciar_demo
from .forms import LeadForm, TicketForm
from .models import Pago, SolicitudDatos
from .utils import ip_del_cliente, pesos, sumar_dias_habiles

MEDIOS_PAGO = ["PSE (débito de cuenta)", "Tarjeta de crédito", "Tarjeta débito", "Transferencia bancaria"]
OTP_MINUTOS = 10


def _cliente(request):
    cliente = getattr(request.user, "cliente", None)
    if cliente is None:
        return None, None
    return cliente, cliente.contratos.first()


def inicio(request):
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save()
            extra = "" if lead.acepta_publicidad else " No le enviaremos publicidad."
            messages.success(request, f"Listo, {lead.nombre.split()[0]}. Le escribiremos a {lead.correo} en máximo 2 días hábiles "
                                      f"para agendar su diagnóstico. Radicado {lead.radicado}.{extra}")
            return redirect("inicio")
    else:
        form = LeadForm(initial={"necesidad": "ventas"})
    return render(request, "portal/inicio.html", {"form": form})


def ingresar(request):
    from django.contrib.auth.views import LoginView
    return LoginView.as_view(template_name="portal/ingresar.html", redirect_authenticated_user=True,
                             extra_context={"demo_usuario": DEMO_USUARIO, "demo_clave": DEMO_CLAVE})(request)


@require_POST
def salir(request):
    logout(request)
    return redirect("inicio")


@login_required
def proyecto(request):
    cliente, contrato = _cliente(request)
    if contrato is None:
        return HttpResponseForbidden("Este usuario no tiene un proyecto asociado.")
    pagos = list(contrato.pagos.all())
    pagados = sum(p.estado == Pago.PAGADO for p in pagos)
    avance = 10 if not contrato.firmado else {0: 20, 1: 60, 2: 85, 3: 100}[pagados]
    hitos = [
        ("1. Diagnóstico y diseño", pagos[0], contrato.firmado),
        ("2. Versión Beta", pagos[1], pagos[0].estado == Pago.PAGADO),
        ("3. Entrega final", pagos[2], pagos[1].estado == Pago.PAGADO),
    ]
    return render(request, "portal/proyecto.html", {
        "cliente": cliente, "contrato": contrato, "avance": avance, "hitos": hitos,
        "valor": pesos(contrato.valor), "proxima": sumar_dias_habiles(timezone.localdate(), 8),
    })


@login_required
def contrato(request):
    cliente, contrato = _cliente(request)
    if contrato is None:
        return HttpResponseForbidden("Este usuario no tiene un contrato asociado.")
    marcado = {"acepta": False, "datos": False}

    if request.method == "POST" and not contrato.firmado:
        accion = request.POST.get("accion")
        marcado = {"acepta": bool(request.POST.get("acepta")), "datos": bool(request.POST.get("datos"))}
        if not marcado["acepta"]:
            messages.error(request, "Marque la casilla \"He leído y acepto el contrato\" para continuar.")
        elif accion == "enviar_otp":
            contrato.otp = f"{secrets.randbelow(900000) + 100000}"
            contrato.otp_creado = timezone.now()
            contrato.save(update_fields=["otp", "otp_creado"])
            messages.success(request, f"Le enviamos un código al correo {request.user.email}. Revise la bandeja simulada.")
        elif accion == "firmar":
            codigo = request.POST.get("codigo", "").strip()
            vencido = contrato.otp_creado and timezone.now() - contrato.otp_creado > timedelta(minutes=OTP_MINUTOS)
            if not marcado["datos"]:
                messages.error(request, "Marque la autorización de datos personales para poder firmar.")
            elif not contrato.otp:
                messages.error(request, "Pulse \"Enviar código a mi correo\" para recibir su código.")
            elif vencido:
                messages.error(request, f"El código venció ({OTP_MINUTOS} minutos). Pida uno nuevo.")
            elif not secrets.compare_digest(codigo, contrato.otp):
                messages.error(request, "El código no coincide. Cópielo de la bandeja de correo e inténtelo otra vez.")
            else:
                ahora = timezone.now()
                contrato.firmado = True
                contrato.firmado_en = ahora
                contrato.ip_firma = ip_del_cliente(request)
                contrato.huella = hashlib.sha256((contrato.texto_para_firmar() + "|" + ahora.isoformat()).encode()).hexdigest()
                contrato.otp = ""
                contrato.save()
                contrato.pagos.filter(orden=1).update(estado=Pago.DISPONIBLE)
                messages.success(request, "Contrato firmado. Ya puede pagar el anticipo.")
                return redirect("contrato")

    return render(request, "portal/contrato.html", {
        "cliente": cliente, "contrato": contrato, "valor": pesos(contrato.valor), "marcado": marcado, "otp_minutos": OTP_MINUTOS,
    })


@login_required
def pagos(request):
    cliente, contrato = _cliente(request)
    if contrato is None:
        return HttpResponseForbidden("Este usuario no tiene pagos asociados.")
    seleccionado = None

    if request.method == "POST":
        pago = get_object_or_404(Pago, pk=request.POST.get("pago"), contrato=contrato)
        if pago.estado != Pago.DISPONIBLE:
            messages.error(request, "Este pago todavía no está habilitado.")
        elif request.POST.get("accion") == "abrir":
            seleccionado = pago
        elif request.POST.get("accion") == "confirmar":
            medio = request.POST.get("medio")
            if medio not in MEDIOS_PAGO:
                messages.error(request, "Escoja un medio de pago.")
                seleccionado = pago
            else:
                pago.estado = Pago.PAGADO
                pago.medio = medio
                pago.pagado_en = timezone.now()
                pago.factura = f"FE-{1020 + pago.pk}"
                pago.save()
                contrato.pagos.filter(orden=pago.orden + 1, estado=Pago.BLOQUEADO).update(estado=Pago.DISPONIBLE)
                messages.success(request, f"Pago aprobado por {medio}. Emitimos la factura electrónica {pago.factura} y se la enviamos a su correo.")
                return redirect("pagos")

    filas = [{"p": p, "valor": pesos(p.valor), "iva": pesos(p.iva), "total": pesos(p.total)} for p in contrato.pagos.all()]
    return render(request, "portal/pagos.html", {
        "contrato": contrato, "filas": filas, "seleccionado": seleccionado,
        "total_sel": pesos(seleccionado.total) if seleccionado else "", "medios": MEDIOS_PAGO,
    })


@login_required
def soporte(request):
    cliente, _ = _cliente(request)
    if cliente is None:
        return HttpResponseForbidden("Este usuario no es cliente.")
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.cliente = cliente
            ticket.save()
            messages.success(request, f"Recibimos su solicitud con el radicado {ticket.radicado}. "
                                      f"Le responderemos antes del {ticket.fecha_limite:%d/%m/%Y}.")
            return redirect("soporte")
    else:
        form = TicketForm(initial={"tipo": "falla", "correo": request.user.email,
                                   "descripcion": "Al registrar una venta, el inventario no se descuenta."})
    return render(request, "portal/soporte.html", {"form": form, "tickets": cliente.tickets.all()})


@login_required
def datos(request):
    cliente, contrato = _cliente(request)
    if cliente is None:
        return HttpResponseForbidden("Este usuario no es cliente.")
    if request.method == "POST":
        accion = request.POST.get("accion")
        if accion == "publicidad":
            cliente.acepta_publicidad = bool(request.POST.get("acepta_publicidad"))
            cliente.save(update_fields=["acepta_publicidad"])
            messages.success(request, "Listo: le enviaremos noticias y ofertas." if cliente.acepta_publicidad
                             else "Listo: ya no le enviaremos publicidad. Seguirá recibiendo los correos de su proyecto.")
        elif accion == "solicitud":
            tipo = request.POST.get("tipo")
            if tipo in SolicitudDatos.PLAZOS:
                sol = SolicitudDatos.objects.create(cliente=cliente, tipo=tipo)
                messages.success(request, f"Recibimos su solicitud. Le responderemos antes del {sol.fecha_limite:%d/%m/%Y}.")
        return redirect("datos")
    return render(request, "portal/datos.html", {
        "cliente": cliente, "contrato": contrato, "solicitudes": cliente.solicitudes.all(), "tipos": SolicitudDatos.TIPOS,
    })


@require_POST
def reiniciar(request):
    """Deja el cliente de ejemplo como nuevo, para volver a mostrar la demostración."""
    crear_o_reiniciar_demo()
    logout(request)
    messages.success(request, "Demostración reiniciada.")
    return redirect("inicio")
