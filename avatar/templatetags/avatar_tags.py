import hashlib

try:
    from urllib.parse import urljoin, urlencode
except ImportError:
    from urlparse import urljoin
    from urllib import urlencode

from django import template
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils import six
from django.utils.translation import ugettext as _

from avatar.conf import settings
from avatar.util import (get_primary_avatar, get_default_avatar_url,
                         cache_result, get_user_model, get_user, force_bytes)
from avatar.models import Avatar

register = template.Library()


@cache_result()
@register.simple_tag
def avatar_url(user, width=settings.AVATAR_DEFAULT_SIZE, height=False, **kwargs):
    if height == False : height = width
    avatar = get_primary_avatar(user, width = width, height = height)
    if avatar:
        return avatar.avatar_url(width, height)

    if settings.AVATAR_GRAVATAR_BACKUP:
        params = {'s': str(width)}
        if settings.AVATAR_GRAVATAR_DEFAULT:
            params['d'] = settings.AVATAR_GRAVATAR_DEFAULT
        path = "%s/?%s" % (hashlib.md5(force_bytes(user.email)).hexdigest(),
                           urlencode(params))
        return urljoin(settings.AVATAR_GRAVATAR_BASE_URL, path)

    return get_default_avatar_url()


@cache_result()
@register.simple_tag
def avatar(user, width=settings.AVATAR_DEFAULT_SIZE, height = False, **kwargs):
    if height == False: height = width
    if not isinstance(user, get_user_model()):
        try:
            user = get_user(user)
            alt = six.text_type(user)
            url = avatar_url(user, width, height)
        except get_user_model().DoesNotExist:
            url = get_default_avatar_url()
            alt = _("Default Avatar")
    else:
        alt = six.text_type(user)
        url = avatar_url(user, width, height)
    context = dict(kwargs, **{
        'user': user,
        'url': url,
        'alt': alt,
        'width': width,
        'height': height
    })
    return render_to_string('avatar/avatar_tag.html', context)


@register.filter
def has_avatar(user):
    if not isinstance(user, get_user_model()):
        return False
    return Avatar.objects.filter(user=user, primary=True).exists()


@cache_result()
@register.simple_tag
def primary_avatar(user, width=settings.AVATAR_DEFAULT_SIZE, height = False):
    """
    This tag tries to get the default avatar for a user without doing any db
    requests. It achieve this by linking to a special view that will do all the
    work for us. If that special view is then cached by a CDN for instance,
    we will avoid many db calls.
    """
    if height == False: height = width
    alt = six.text_type(user)
    url = reverse('avatar_render_primary', kwargs={'user': user, 'width': width, 'height': height})
    return ("""<img src="%s" alt="%s" width="%s" height="%s" />""" %
            (url, alt, width, height))


@cache_result()
@register.simple_tag
def render_avatar(avatar, width=settings.AVATAR_DEFAULT_SIZE, height = False):
    if height == False: height = width
    if not avatar.thumbnail_exists(width, height):
        avatar.create_thumbnail(width, height)
    return """<img src="%s" alt="%s" width="%s" height="%s" />""" % (
        avatar.avatar_url(width, height), six.text_type(avatar), width, height)


@register.tag
def primary_avatar_object(parser, token):
    split = token.split_contents()
    if len(split) == 4:
        return UsersAvatarObjectNode(split[1], split[3])
    raise template.TemplateSyntaxError('%r tag takes three arguments.' %
                                       split[0])


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
        return six.text_type()
