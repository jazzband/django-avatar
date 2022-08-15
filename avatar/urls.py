from django.urls import re_path

from avatar import views

urlpatterns = [
    re_path(r"^add/$", views.add, name="avatar_add"),
    re_path(r"^change/$", views.change, name="avatar_change"),
    re_path(r"^delete/$", views.delete, name="avatar_delete"),
    re_path(
        r"^render_primary/(?P<user>[\w\d\@\.\-_]+)/(?P<width>[\d]+)/$",
        views.render_primary,
        name="avatar_render_primary",
    ),
    re_path(
        r"^render_primary/(?P<user>[\w\d\@\.\-_]+)/(?P<width>[\d]+)/(?P<height>[\d]+)/$",
        views.render_primary,
        name="avatar_render_primary",
    ),
]
