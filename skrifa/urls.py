from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Skrifa Labs S.A.S. · Administración"
admin.site.site_title = "Skrifa Labs"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("portal.urls")),
]
