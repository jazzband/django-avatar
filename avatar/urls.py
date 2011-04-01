from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('avatar.views',
    url('^add/$', 'add', name='avatar_add'),
    url('^webcam-upload/(?P<id>\d+)', 'webcam_upload', name='avatar-webcam-upload'),
    url('^change/$', 'change', name='avatar_change'),
    url('^delete/$', 'delete', name='avatar_delete'),
    url('^render_primary/(?P<user>[\+\w]+)/(?P<size>[\d]+)/$', 'render_primary', name='avatar_render_primary'),
    
    url('^list/(?P<username>[\+\w]+)/$', 'avatar_gallery', name='avatar_gallery'),
    url('^list/(?P<username>[\+\w]+)/(?P<id>[\d]+)/$', 'avatar', name='avatar'),
)
