import urllib

from django import template
from django.utils.translation import ugettext as _
from django.utils.hashcompat import md5_constructor
from django.core.urlresolvers import reverse

from avatar.settings import (AVATAR_GRAVATAR_BACKUP, AVATAR_GRAVATAR_DEFAULT,
                             AVATAR_DEFAULT_SIZE)
from avatar.util import (get_primary_avatar, get_default_avatar_url,
                         cache_result, get_target_gravatar_url, get_target_handler)

register = template.Library()

@cache_result
@register.simple_tag
def avatar_url(target, size=AVATAR_DEFAULT_SIZE):
    avatar = get_primary_avatar(target)
    if avatar:
        if not avatar.thumbnail_exists(size):
            avatar.create_thumbnail(size)
        return avatar.avatar_url(size)
    else:
        if AVATAR_GRAVATAR_BACKUP:
            params = {'s': str(size)}
            if AVATAR_GRAVATAR_DEFAULT:
                params['d'] = AVATAR_GRAVATAR_DEFAULT
            return "http://www.gravatar.com/avatar/%s/?%s" % (
                md5_constructor(get_target_gravatar_url(target)).hexdigest(),
                urllib.urlencode(params))
        else:
            return get_default_avatar_url(target, size)

@cache_result
@register.simple_tag
def avatar(target, size=AVATAR_DEFAULT_SIZE):
    handler = get_target_handler()
    obj = handler.get_target_object(target)

    if not obj:
        url = get_default_avatar_url(target, size)
        alt = _("Default Avatar")
    else:
        url = avatar_url(obj, size)
        alt = handler.get_alt_text(obj)
    return """<img src="%s" alt="%s" width="%s" height="%s" />""" % (url, alt,
                                                                     size, size)

@cache_result
@register.simple_tag
def primary_avatar(target, size=AVATAR_DEFAULT_SIZE):
    """
    This tag tries to get the default avatar for a user without doing any db
    requests. It achieve this by linking to a special view that will do all the 
    work for us. If that special view is then cached by a CDN for instance,
    we will avoid many db calls.
    """
    handler = get_target_handler()
    alt = handler.get_alt_text(target)
    type = handler.get_type(target)
    id = handler.get_id(target)
    url = reverse('avatar_render_primary', kwargs={'target_type' : type, 'id': id, 'size' : size})
    return """<img src="%s" alt="%s" width="%s" height="%s" />""" % (url, alt,
        size, size)

@cache_result
@register.simple_tag
def render_avatar(avatar, size=AVATAR_DEFAULT_SIZE):
    if not avatar.thumbnail_exists(size):
        avatar.create_thumbnail(size)
    return "<img src='%s' alt='%s' width='%s' height='%s' />" % (
        avatar.avatar_url(size), unicode(avatar), size, size)
