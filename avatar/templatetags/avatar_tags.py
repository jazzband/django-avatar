from django import template
try:
    from django.urls import reverse
except ImportError:
    # For Django < 1.10
    from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
# Issue 182: six no longer included with Django 3.0
try:
    from django.utils import six
except ImportError:
    import six
from django.utils.translation import ugettext as _
from django.utils.module_loading import import_string

from avatar.conf import settings
from avatar.models import Avatar
from avatar.utils import (
    cache_result,
    get_default_avatar_url,
    get_user_model,
    get_user,
)


register = template.Library()


@cache_result()
@register.simple_tag
def avatar_url(user, size=settings.AVATAR_DEFAULT_SIZE):
    for provider_path in settings.AVATAR_PROVIDERS:
        provider = import_string(provider_path)
        avatar_url = provider.get_avatar_url(user, size)
        if avatar_url:
            return avatar_url


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
    kwargs.update({'alt': alt})

    context = {
        'user': user,
        'url': url,
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
