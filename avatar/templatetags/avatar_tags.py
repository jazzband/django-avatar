import urllib

from django import template
from django.utils.translation import ugettext as _
from django.utils.hashcompat import md5_constructor
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User

from avatar.settings import (AVATAR_GRAVATAR_BACKUP, AVATAR_GRAVATAR_DEFAULT,
                             AVATAR_DEFAULT_SIZE)
from avatar.util import get_primary_avatar, get_default_avatar_url, cache_result

register = template.Library()


@cache_result
@register.simple_tag
def avatar_url(user, width=AVATAR_DEFAULT_SIZE, height=False):
    if height == False: height = width
    avatar = get_primary_avatar(user, width=width, height=height)
    if avatar:
        return avatar.avatar_url(width,height)
    else:
        if AVATAR_GRAVATAR_BACKUP:
            params = {'s': str(width)}
            if AVATAR_GRAVATAR_DEFAULT:
                params['d'] = AVATAR_GRAVATAR_DEFAULT
            return "http://www.gravatar.com/avatar/%s/?%s" % (
                md5_constructor(user.email).hexdigest(),
                urllib.urlencode(params))
        else:
            return get_default_avatar_url()

@cache_result
@register.simple_tag
def avatar(user, width=AVATAR_DEFAULT_SIZE, height=False):
    if height == False: height = width
    if not isinstance(user, User):
        try:
            user = User.objects.get(username=user)
            alt = unicode(user)
            url = avatar_url(user, width, height)
        except User.DoesNotExist:
            url = get_default_avatar_url()
            alt = _("Default Avatar")
    else:
        alt = unicode(user)
        url = avatar_url(user, width, height)
    return """<img src="%s" alt="%s" width="%s" height="%s" />""" % (url, alt, width, height)

@cache_result
@register.simple_tag
def primary_avatar(user, width=AVATAR_DEFAULT_SIZE, height=False):
    if height == False: height = width
    """
    This tag tries to get the default avatar for a user without doing any db
    requests. It achieve this by linking to a special view that will do all the 
    work for us. If that special view is then cached by a CDN for instance,
    we will avoid many db calls.
    """
    alt = unicode(user)
    url = reverse('avatar_render_primary', kwargs={'user' : user, 'width' : width, 'height' : height})
    return """<img src="%s" alt="%s" width="%s" height="%s" class="avatar" />""" % (url, alt, width, height)

@cache_result
@register.simple_tag
def large_avatar(user,class_name="",id_name=""):
    """
    This tag tries to get the default avatar for a user without doing any db
    requests. It achieve this by linking to a special view that will do all the 
    work for us. If that special view is then cached by a CDN for instance,
    we will avoid many db calls.
    """
    alt = unicode(user)
    url = reverse('avatar_render_primary', kwargs={'user' : user, 'width' : 0, 'height' : 0})
    return """<img src="%s" class="%s" id="%s" />""" % (url,class_name,id_name)

@cache_result
@register.simple_tag
def render_avatar(avatar, width=AVATAR_DEFAULT_SIZE, height=False):
    if height == False: height = width
    if not avatar.thumbnail_exists(width,height):
        avatar.create_thumbnail(width,height)
    return """<img src="%s" alt="%s" width="%s" height="%s" />""" % (
        avatar.avatar_url(width, height), str(avatar), width, height)
