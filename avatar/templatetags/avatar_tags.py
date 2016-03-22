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
from django.utils.module_loading import import_string

from avatar.conf import settings
from avatar.utils import (get_primary_avatar, get_default_avatar_url,
                          cache_result, get_user_model, get_user, force_bytes)
from avatar.models import Avatar

register = template.Library()

get_facebook_id = None

if settings.AVATAR_FACEBOOK_BACKUP:
    if callable(settings.AVATAR_FACEBOOK_GET_ID):
        get_facebook_id = settings.AVATAR_FACEBOOK_GET_ID
    else:
        get_facebook_id = import_string(settings.AVATAR_FACEBOOK_GET_ID)


@cache_result()
@register.simple_tag
def avatar_url(user, size=settings.AVATAR_DEFAULT_SIZE):
    avatar = get_primary_avatar(user, size=size)
    if avatar:
        return avatar.avatar_url(size)

    if settings.AVATAR_GRAVATAR_BACKUP:
        params = {'s': str(size)}
        if settings.AVATAR_GRAVATAR_DEFAULT:
            params['d'] = settings.AVATAR_GRAVATAR_DEFAULT
        if settings.AVATAR_GRAVATAR_FORCEDEFAULT:
            params['f'] = 'y'
        path = "%s/?%s" % (hashlib.md5(force_bytes(getattr(user,
            settings.AVATAR_GRAVATAR_FIELD))).hexdigest(), urlencode(params))
        return urljoin(settings.AVATAR_GRAVATAR_BASE_URL, path)

    if settings.AVATAR_FACEBOOK_BACKUP:
        fb_id = get_facebook_id(user)
        if fb_id:
            return 'https://graph.facebook.com/{fb_id}/picture?type=square&width={size}&height={size}'.format(
                fb_id=fb_id, size=size
            )

    return get_default_avatar_url()


@cache_result()
@register.simple_tag
def avatar(user, size=settings.AVATAR_DEFAULT_SIZE, **kwargs):
    if not isinstance(user, get_user_model()):
        try:
            user = get_user(user)
            alt = six.text_type(user)
            url = avatar_url(user, size)
        except get_user_model().DoesNotExist:
            url = get_default_avatar_url()
            alt = _("Default Avatar")
    else:
        alt = six.text_type(user)
        url = avatar_url(user, size)
    context = {
        'user': user,
        'url': url,
        'alt': alt,
        'size': size,
        'kwargs': kwargs,
    }
    return render_to_string('avatar/avatar_tag.html', context)


@register.filter
def has_avatar(user):
    if not isinstance(user, get_user_model()):
        return False
    return Avatar.objects.filter(user=user, primary=True).exists()


@cache_result()
@register.simple_tag
def primary_avatar(user, size=settings.AVATAR_DEFAULT_SIZE):
    """
    This tag tries to get the default avatar for a user without doing any db
    requests. It achieve this by linking to a special view that will do all the
    work for us. If that special view is then cached by a CDN for instance,
    we will avoid many db calls.
    """
    alt = six.text_type(user)
    url = reverse('avatar_render_primary', kwargs={'user': user, 'size': size})
    return ("""<img src="%s" alt="%s" width="%s" height="%s" />""" %
            (url, alt, size, size))


@cache_result()
@register.simple_tag
def render_avatar(avatar, size=settings.AVATAR_DEFAULT_SIZE):
    if not avatar.thumbnail_exists(size):
        avatar.create_thumbnail(size)
    return """<img src="%s" alt="%s" width="%s" height="%s" />""" % (
        avatar.avatar_url(size), six.text_type(avatar), size, size)


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
