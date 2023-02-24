from django.urls import path

from avatar import views

# For reversing namespaced urls
# https://docs.djangoproject.com/en/4.1/topics/http/urls/#reversing-namespaced-urls
app_name = "avatar"

urlpatterns = [
    path("add/", views.add, name="add"),
    path("change/", views.change, name="change"),
    path("delete/", views.delete, name="delete"),
    # https://docs.djangoproject.com/en/4.1/topics/http/urls/#path-converters
    path(
        "render_primary/<slug:user>/<int:width>/",
        views.render_primary,
        name="render_primary",
    ),
    path(
        "render_primary/<slug:user>/<int:width>/<int:height>/",
        views.render_primary,
        name="render_primary",
    ),
]
