import hashlib

try:
    from urllib.parse import urljoin, urlencode
except ImportError:
    from urlparse import urljoin
    from urllib import urlencode


from avatar.conf import settings
from avatar.utils import (
    force_bytes,
    get_default_avatar_url,
    get_primary_avatar,
)

from django.utils.module_loading import import_string

# If the FacebookAvatarProvider is used, a mechanism needs to be defined on
# how to obtain the user's Facebook UID. This is done via
# ``AVATAR_FACEBOOK_GET_ID``.
get_facebook_id = None

if 'avatar.providers.FacebookAvatarProvider' in settings.AVATAR_PROVIDERS:
    if callable(settings.AVATAR_FACEBOOK_GET_ID):
        get_facebook_id = settings.AVATAR_FACEBOOK_GET_ID
    else:
        get_facebook_id = import_string(settings.AVATAR_FACEBOOK_GET_ID)


class DefaultAvatarProvider(object):
    """
    Returns the default url defined by ``settings.DEFAULT_AVATAR_URL``.
    """

    @classmethod
    def get_avatar_url(cls, user, size):
        return get_default_avatar_url()


class PrimaryAvatarProvider(object):
    """
    Returns the primary Avatar from the users avatar set.
    """

    @classmethod
    def get_avatar_url(cls, user, size):
        avatar = get_primary_avatar(user, size)
        if avatar:
            return avatar.avatar_url(size)


class GravatarAvatarProvider(object):
    """
    Returns the url for an avatar by the Gravatar service.
    """

    @classmethod
    def get_avatar_url(cls, user, size):
        params = {'s': str(size)}
        if settings.AVATAR_GRAVATAR_DEFAULT:
            params['d'] = settings.AVATAR_GRAVATAR_DEFAULT
        if settings.AVATAR_GRAVATAR_FORCEDEFAULT:
            params['f'] = 'y'
        path = "%s/?%s" % (hashlib.md5(force_bytes(getattr(user,
            settings.AVATAR_GRAVATAR_FIELD))).hexdigest(), urlencode(params))

        return urljoin(settings.AVATAR_GRAVATAR_BASE_URL, path)


class FacebookAvatarProvider(object):
    """
    Returns the url of a Facebook profile image.
    """

    @classmethod
    def get_avatar_url(cls, user, size):
        fb_id = get_facebook_id(user)
        if fb_id:
            url = 'https://graph.facebook.com/{fb_id}/picture?type=square&width={size}&height={size}'
            return url.format(
                fb_id=fb_id,
                size=size
            )


class InitialsAvatarProvider(object):
    """
    Returns a tuple with template_name and context for rendering the given user's avatar as their
    initials in white against a background with random hue based on their primary key.
    """

    @classmethod
    def get_avatar_url(cls, user, size):
        initials = user.first_name[:1] + user.last_name[:1]
        if not initials:
            initials = user.username[:1]
        initials = initials.upper()
        context = {
            'fontsize': (size * 1.1) / 2,
            'initials': initials,
            'hue': user.pk % 360,
            'saturation': '65%',
            'lightness': '60%',
        }
        return ('avatar/initials.html', context)
