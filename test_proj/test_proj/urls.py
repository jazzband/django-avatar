from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.static import serve

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^avatar/", include("avatar.urls")),
]


if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += [
        url(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT})
    ]
