try:
    from django.conf.urls import patterns, url
except ImportError:
    # Django < 1.4
    from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('avatar.views',
    url(r'^add/$', 'add', name='avatar_add'),
    url(r'^change/$', 'change', name='avatar_change'),
    url(r'^delete/$', 'delete', name='avatar_delete'),
    url(r'^render_primary/(?P<user>[\w\d\.\-_]{3,30})/(?P<size>[\d]+)/$', 'render_primary', name='avatar_render_primary'),
    url(r'^list/(?P<username>[\+\w\@\.]+)/$', 'avatar_gallery', name='avatar_gallery'),
    url(r'^list/(?P<username>[\+\w\@\.]+)/(?P<id>[\d]+)/$', 'avatar', name='avatar'),

    url(r'^add_for_user/(?P<for_user>[\w@\.\+\-_]+)/$',
        'add_avatar_for_user', name='avatar_add_for_user'),
    url(r'^change_for_user/(?P<for_user>[\w@\.\+\-_]+)/$',
        'change_avatar_for_user', name='avatar_change_for_user'),
    url(r'^delete_for_user/(?P<for_user>[\w@\.\+\-_]+)/$',
        'delete_avatar_for_user', name='avatar_delete_for_user'),
)
