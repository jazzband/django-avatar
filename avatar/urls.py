from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('avatar.views',
    url('^add/$', 'add', name='avatar_add'),
    url('^change/$', 'change', name='avatar_change'),
    url('^delete/$', 'delete', name='avatar_delete'),

    url('^(?P<target_type>\w+)/(?P<target_id>\d+)/add/$', 'add', name='avatar_add_generic'),
    url('^(?P<target_type>\w+)/(?P<target_id>\d+)/change/$', 'change', name='avatar_change_generic'),
    url('^(?P<target_type>\w+)/(?P<target_id>\d+)/delete/$', 'delete', name='avatar_delete_generic'),

    url('^(?P<target_type>\w+)/(?P<target_id>\d+)/render_primary/(?P<size>[\d]+)/$', 'render_primary', name='avatar_render_primary'),
)
