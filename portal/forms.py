from django import forms

from .models import Lead, Ticket


class LeadForm(forms.ModelForm):
    autoriza_datos = forms.BooleanField(
        required=True,
        label="Autorizo a Skrifa Labs S.A.S. a tratar mis datos para agendar el diagnóstico y enviarme la propuesta (Ley 1581 de 2012).",
        error_messages={"required": "Para continuar, marque la casilla de autorización de datos. Sin ella no podemos contactarlo."},
    )

    class Meta:
        model = Lead
        fields = ["nombre", "negocio", "correo", "necesidad", "autoriza_datos", "acepta_publicidad"]
        labels = {
            "nombre": "Nombre completo",
            "negocio": "Nombre del negocio",
            "correo": "Correo electrónico",
            "necesidad": "¿Qué quiere mejorar?",
            "acepta_publicidad": "Quiero recibir noticias y ofertas (opcional).",
        }


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["tipo", "descripcion", "correo"]
        labels = {"tipo": "Tipo de solicitud", "descripcion": "Describa la situación", "correo": "Correo de contacto"}
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 4})}

    def clean_descripcion(self):
        texto = self.cleaned_data["descripcion"].strip()
        if len(texto) < 10:
            raise forms.ValidationError("Cuéntenos un poco más del problema (mínimo 10 caracteres) para poder ayudarle.")
        return texto
