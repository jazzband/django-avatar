from django.urls import include, re_path

urlpatterns = [
    re_path(r"^avatar/", include("avatar.urls")),
]
