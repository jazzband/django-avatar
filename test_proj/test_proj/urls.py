from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^avatar/", include("avatar.urls")),
    re_path(r"^api/", include('avatar.api.urls')),
]


if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT})
    ]
