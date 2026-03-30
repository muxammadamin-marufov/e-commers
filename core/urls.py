from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Google tasdiqlash fayli uchun yo'l
    path(
        "google87cf84e6be0bf571.html",
        TemplateView.as_view(template_name="google87cf84e6be0bf571.html", content_type="text/html"),
    ),
    path('admin/', admin.site.urls),
    path('', include("market.urls")),
]

# Media fayllar (rasmlar) uchun sozlama
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)