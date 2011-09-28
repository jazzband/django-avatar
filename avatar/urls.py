from django.conf.urls.defaults import patterns, url
from avatar.views import (AddAvatarView, ChangeAvatarView, DeleteAvatarView,
                          PrimaryAvatarView)

urlpatterns = patterns('',
    url('^add/$', AddAvatarView.as_view(), name='avatar_add'),
    url('^change/$', ChangeAvatarView.as_view(), name='avatar_change'),
    url('^delete/$', DeleteAvatarView.as_view(), name='avatar_delete'),
    url('^render_primary/(?P<user>[\+\w]+)/(?P<size>[\d]+)/$',
        PrimaryAvatarView.as_view(), name='avatar_render_primary'),
)
