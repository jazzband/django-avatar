from django.urls import path, re_path

from avatar import views

# For reverseing namespaced urls
# https://docs.djangoproject.com/en/4.1/topics/http/urls/#reversing-namespaced-urls
app_name = "avatar"

urlpatterns = [
    path("add/", views.add, name="avatar_add"),
    path("change/", views.change, name="avatar_change"),
    path("delete/", views.delete, name="avatar_delete"),
    # https://docs.djangoproject.com/en/4.1/topics/http/urls/#path-converters
    path(
        "render_primary/<slug:user>/<int:width>/",
        views.render_primary,
        name="avatar_render_primary",
    ),
    re_path(
        "render_primary/<slug:user>/<int:width>/<int:height>",
        views.render_primary,
        name="avatar_render_primary",
    ),
]
