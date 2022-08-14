from django import template
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _

from avatar.conf import settings
from avatar.models import Avatar
from avatar.utils import cache_result, get_default_avatar_url, get_user, get_user_model

register = template.Library()


@cache_result()
@register.simple_tag
def avatar_url(user, width=settings.AVATAR_DEFAULT_SIZE, height=False):
    if height is False:
        height = width
    for provider_path in settings.AVATAR_PROVIDERS:
        provider = import_string(provider_path)
        avatar_url = provider.get_avatar_url(user, width, height)
        if avatar_url:
            return avatar_url


@cache_result()
@register.simple_tag
def avatar(user, width=settings.AVATAR_DEFAULT_SIZE, height=False, **kwargs):
    if height is False:
        height = width
    if not isinstance(user, get_user_model()):
        try:
            user = get_user(user)
            if settings.AVATAR_EXPOSE_USERNAMES:
                alt = str(user)
            else:
                alt = _("User Avatar")
            url = avatar_url(user, width, height)
        except get_user_model().DoesNotExist:
            url = get_default_avatar_url()
            alt = _("Default Avatar")
    else:
        if settings.AVATAR_EXPOSE_USERNAMES:
            alt = str(user)
        else:
            alt = _("User Avatar")
        url = avatar_url(user, width, height)
    kwargs.update({"alt": alt})

    context = {
        "user": user,
        "alt": alt,
        "width": width,
        "height": height,
        "kwargs": kwargs,
    }
    template_name = "avatar/avatar_tag.html"
    ext_context = None
    try:
        template_name, ext_context = url
    except ValueError:
        context["url"] = url
    if ext_context:
        context = dict(context, **ext_context)
    return render_to_string(template_name, context)


@register.filter
def has_avatar(user):
    if not isinstance(user, get_user_model()):
        return False
    return Avatar.objects.filter(user=user, primary=True).exists()


@cache_result()
@register.simple_tag
def primary_avatar(user, width=settings.AVATAR_DEFAULT_SIZE, height=False):
    """
    This tag tries to get the default avatar for a user without doing any db
    requests. It achieve this by linking to a special view that will do all the
    work for us. If that special view is then cached by a CDN for instance,
    we will avoid many db calls.
    """
    if height is False:
        height = width
    alt = str(user)
    url = reverse(
        "avatar_render_primary", kwargs={"user": user, "width": width, "height": height}
    )
    return """<img src="%s" alt="%s" width="%s" height="%s" />""" % (
        url,
        alt,
        width,
        height,
    )


@cache_result()
@register.simple_tag
def render_avatar(avatar, width=settings.AVATAR_DEFAULT_SIZE, height=False):
    if height is False:
        height = width
    if not avatar.thumbnail_exists(width, height):
        avatar.create_thumbnail(width, height)
    return """<img src="%s" alt="%s" width="%s" height="%s" />""" % (
        avatar.avatar_url(width, height),
        str(avatar),
        width,
        height,
    )


@register.tag
def primary_avatar_object(parser, token):
    split = token.split_contents()
    if len(split) == 4:
        return UsersAvatarObjectNode(split[1], split[3])
    raise template.TemplateSyntaxError("%r tag takes three arguments." % split[0])


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
        return str()
