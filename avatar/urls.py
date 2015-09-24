try:
    from django.conf.urls import patterns, url
except ImportError:
    # Django < 1.4
    from django.conf.urls.defaults import patterns, url

from avatar import views

urlpatterns = patterns('',
    url(r'^add/$', views.add, name='avatar_add'),
    url(r'^change/$', views.change, name='avatar_change'),
    url(r'^delete/$', views.delete, name='avatar_delete'),
    url(r'^render_primary/(?P<user>[\w\d\@\.\-_]{3,30})/(?P<size>[\d]+)/$',
        views.render_primary,
        name='avatar_render_primary'),
    url(r'^list/(?P<username>[\+\w\@\.]+)/$',
        views.avatar_gallery,
        name='avatar_gallery'),
    url(r'^list/(?P<username>[\+\w\@\.]+)/(?P<id>[\d]+)/$',
        views.avatar,
        name='avatar'),
)
