import urllib
import urlparse
import hashlib

from django import template
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from avatar.settings import (AVATAR_GRAVATAR_BACKUP, AVATAR_GRAVATAR_DEFAULT,
                             AVATAR_DEFAULT_SIZE, AVATAR_GRAVATAR_BASE_URL)
from avatar.util import (
    get_primary_avatar, get_default_avatar_url, cache_result, User, get_user)
from avatar.models import Avatar

register = template.Library()


@cache_result
@register.simple_tag
def avatar_url(user, size=AVATAR_DEFAULT_SIZE):
    avatar = get_primary_avatar(user, size=size)
    if avatar:
        return avatar.avatar_url(size)

    if AVATAR_GRAVATAR_BACKUP:
        params = {'s': str(size)}
        if AVATAR_GRAVATAR_DEFAULT:
            params['d'] = AVATAR_GRAVATAR_DEFAULT
        path = "%s/?%s" % (hashlib.md5(user.email).hexdigest(),
                           urllib.urlencode(params))
        return urlparse.urljoin(AVATAR_GRAVATAR_BASE_URL, path)

    return get_default_avatar_url()


@cache_result
@register.simple_tag
def avatar(user, size=AVATAR_DEFAULT_SIZE, **kwargs):
    if not isinstance(user, User):
        try:
            user = get_user(user)
            alt = unicode(user)
            url = avatar_url(user, size)
        except User.DoesNotExist:
            url = get_default_avatar_url()
            alt = _("Default Avatar")
    else:
        alt = unicode(user)
        url = avatar_url(user, size)
    context = dict(kwargs, **{
        'user': user,
        'url': url,
        'alt': alt,
        'size': size,
    })
    return render_to_string('avatar/avatar_tag.html', context)


@register.filter
def has_avatar(user):
    if not isinstance(user, User):
        return False
    return Avatar.objects.filter(user=user, primary=True).exists()


@cache_result
@register.simple_tag
def primary_avatar(user, size=AVATAR_DEFAULT_SIZE):
    """
    This tag tries to get the default avatar for a user without doing any db
    requests. It achieve this by linking to a special view that will do all the
    work for us. If that special view is then cached by a CDN for instance,
    we will avoid many db calls.
    """
    alt = unicode(user)
    url = reverse('avatar_render_primary', kwargs={'user': user, 'size': size})
    return """<img src="%s" alt="%s" width="%s" height="%s" />""" % (url, alt,
        size, size)


@cache_result
@register.simple_tag
def render_avatar(avatar, size=AVATAR_DEFAULT_SIZE):
    if not avatar.thumbnail_exists(size):
        avatar.create_thumbnail(size)
    return """<img src="%s" alt="%s" width="%s" height="%s" />""" % (
        avatar.avatar_url(size), str(avatar), size, size)


def primary_avatar_object(parser, token):
    split = token.split_contents()
    if len(split) == 4:
        return UsersAvatarObjectNode(split[1], split[3])
    else:
        raise template.TemplateSyntaxError('%r tag takes three arguments.' % split[0])


class UsersAvatarObjectNode(template.Node):
    def __init__(self, user, key):
        self.user = template.Variable(user)
        self.key = key

    def render(self, context):
        user = self.user.resolve(context)
        key = self.key
        avatar = Avatar.objects.filter(user=user, primary=True)
        if avatar:
            context[key] = avatar[0]
        else:
            context[key] = None
        return u""

register.tag('primary_avatar_object', primary_avatar_object)
