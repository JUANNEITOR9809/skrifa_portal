# Portal de Clientes · Skrifa Labs S.A.S.

Aplicación Django del proyecto final de Aspectos Legales, Comerciales y Éticos de la Profesión (UAN).
Muestra lo que hace la empresa: diagnóstico gratis, firma electrónica del contrato con código OTP
(Ley 527 de 1999), pagos por hitos con factura electrónica, tickets de soporte (PQR) y derechos
de datos personales (Ley 1581 de 2012).

## Correr en el computador (Windows)

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py crear_demo
python manage.py createsuperuser   (opcional, para entrar a /admin)
python manage.py runserver
```

Abrir http://127.0.0.1:8000

Usuario de ejemplo: gerencia@ferreteriaeltornillo.co · Contraseña: Tornillo2026

## Publicar en Render

1. Subir esta carpeta a un repositorio de GitHub.
2. En Render: New → Blueprint → escoger el repositorio (usa `render.yaml`).
3. Render crea el servicio web gratis, genera SECRET_KEY y pone DEBUG=False.

En el plan gratis la base SQLite se reinicia en cada despliegue: es suficiente para la demostración.
