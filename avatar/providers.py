import hashlib
import re
from urllib.parse import urlencode, urljoin

import dns.resolver
from django.utils.module_loading import import_string

from avatar.conf import settings
from avatar.utils import force_bytes, get_default_avatar_url, get_primary_avatar

# If the FacebookAvatarProvider is used, a mechanism needs to be defined on
# how to obtain the user's Facebook UID. This is done via
# ``AVATAR_FACEBOOK_GET_ID``.
get_facebook_id = None

if "avatar.providers.FacebookAvatarProvider" in settings.AVATAR_PROVIDERS:
    if callable(settings.AVATAR_FACEBOOK_GET_ID):
        get_facebook_id = settings.AVATAR_FACEBOOK_GET_ID
    else:
        get_facebook_id = import_string(settings.AVATAR_FACEBOOK_GET_ID)


class DefaultAvatarProvider(object):
    """
    Returns the default url defined by ``settings.DEFAULT_AVATAR_URL``.
    """

    @classmethod
    def get_avatar_url(cls, user, width, height=None):
        return get_default_avatar_url()


class PrimaryAvatarProvider(object):
    """
    Returns the primary Avatar from the users avatar set.
    """

    @classmethod
    def get_avatar_url(cls, user, width, height=None):
        if not height:
            height = width
        avatar = get_primary_avatar(user, width, height)
        if avatar:
            return avatar.avatar_url(width, height)


class GravatarAvatarProvider(object):
    """
    Returns the url for an avatar by the Gravatar service.
    """

    @classmethod
    def get_avatar_url(cls, user, width, _height=None):
        params = {"s": str(width)}
        if settings.AVATAR_GRAVATAR_DEFAULT:
            params["d"] = settings.AVATAR_GRAVATAR_DEFAULT
        if settings.AVATAR_GRAVATAR_FORCEDEFAULT:
            params["f"] = "y"
        path = "%s/?%s" % (
            hashlib.md5(
                force_bytes(getattr(user, settings.AVATAR_GRAVATAR_FIELD))
            ).hexdigest(),
            urlencode(params),
        )

        return urljoin(settings.AVATAR_GRAVATAR_BASE_URL, path)


class LibRAvatarProvider:
    """
    Returns the url of an avatar by the Ravatar service.
    """

    @classmethod
    def get_avatar_url(cls, user, width, _height=None):
        email = getattr(user, settings.AVATAR_GRAVATAR_FIELD).encode("utf-8")
        _, domain = email.split(b"@")
        try:
            answers = dns.resolver.query("_avatars._tcp." + domain, "SRV")
            hostname = re.sub(r"\.$", "", str(answers[0].target))
            # query returns "example.com." and while http requests are fine with this,
            # https most certainly do not consider "example.com." and "example.com" to be the same.
            port = str(answers[0].port)
            if port == "443":
                baseurl = "https://" + hostname + "/avatar/"
            else:
                baseurl = "http://" + hostname + ":" + port + "/avatar/"
        except Exception:
            baseurl = "https://seccdn.libravatar.org/avatar/"
        hash = hashlib.md5(email.strip().lower()).hexdigest()
        return baseurl + hash


class FacebookAvatarProvider(object):
    """
    Returns the url of a Facebook profile image.
    """

    @classmethod
    def get_avatar_url(cls, user, width, height=None):
        if not height:
            height = width
        fb_id = get_facebook_id(user)
        if fb_id:
            url = "https://graph.facebook.com/{fb_id}/picture?type=square&width={width}&height={height}"
            return url.format(fb_id=fb_id, width=width, height=height)


class InitialsAvatarProvider(object):
    """
    Returns a tuple with template_name and context for rendering the given user's avatar as their
    initials in white against a background with random hue based on their primary key.
    """

    @classmethod
    def get_avatar_url(cls, user, width, _height=None):
        initials = user.first_name[:1] + user.last_name[:1]
        if not initials:
            initials = user.username[:1]
        initials = initials.upper()
        context = {
            "fontsize": (width * 1.1) / 2,
            "initials": initials,
            "hue": user.pk % 360,
            "saturation": "65%",
            "lightness": "60%",
        }
        return ("avatar/initials.html", context)
