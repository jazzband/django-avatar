from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('avatar.views',
    url('^add/$', 'add', name='avatar_add'),
    url('^change/$', 'change', name='avatar_change'),
    url('^delete/$', 'delete', name='avatar_delete'),
)
