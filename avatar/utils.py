import hashlib

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.template.defaultfilters import slugify
from django.utils.encoding import force_bytes

from avatar.conf import settings

cached_funcs = set()


def get_username(user):
    """Return username of a User instance"""
    if hasattr(user, "get_username"):
        return user.get_username()
    else:
        return user.username


def get_user(username):
    """Return user from a username/ish identifier"""
    return get_user_model().objects.get_by_natural_key(username)


def get_cache_key(user_or_username, width, height, prefix):
    """
    Returns a cache key consisten of a username and image size.
    """
    if isinstance(user_or_username, get_user_model()):
        user_or_username = get_username(user_or_username)
    key = "%s_%s_%s_%s" % (prefix, user_or_username, width, height or width)
    return "%s_%s" % (
        slugify(key)[:100],
        hashlib.md5(force_bytes(key)).hexdigest(),
    )


def cache_set(key, value):
    cache.set(key, value, settings.AVATAR_CACHE_TIMEOUT)
    return value


def cache_result(default_size=settings.AVATAR_DEFAULT_SIZE):
    """
    Decorator to cache the result of functions that take a ``user``, a
    ``width`` and a ``height`` value.
    """
    if not settings.AVATAR_CACHE_ENABLED:

        def decorator(func):
            return func

        return decorator

    def decorator(func):
        def cached_func(user, width=None, height=None, **kwargs):
            prefix = func.__name__
            cached_funcs.add(prefix)
            key = get_cache_key(user, width or default_size, height, prefix=prefix)
            result = cache.get(key)
            if result is None:
                result = func(user, width or default_size, height, **kwargs)
                cache_set(key, result)
            return result

        return cached_func

    return decorator


def invalidate_cache(user, width=None, height=None):
    """
    Function to be called when saving or changing a user's avatars.
    """
    sizes = set(settings.AVATAR_AUTO_GENERATE_SIZES)
    if width is not None:
        sizes.add((width, height or width))
    for prefix in cached_funcs:
        for size in sizes:
            if isinstance(size, int):
                cache.delete(get_cache_key(user, size, size, prefix))
            else:
                # Size is specified with height and width.
                cache.delete(get_cache_key(user, size[0], size[1], prefix))


def get_default_avatar_url():
    base_url = getattr(settings, "STATIC_URL", None)
    if not base_url:
        base_url = getattr(settings, "MEDIA_URL", "")

    # Don't use base_url if the default url starts with http:// of https://
    if settings.AVATAR_DEFAULT_URL.startswith(("http://", "https://")):
        return settings.AVATAR_DEFAULT_URL
    # We'll be nice and make sure there are no duplicated forward slashes
    ends = base_url.endswith("/")

    begins = settings.AVATAR_DEFAULT_URL.startswith("/")
    if ends and begins:
        base_url = base_url[:-1]
    elif not ends and not begins:
        return "%s/%s" % (base_url, settings.AVATAR_DEFAULT_URL)

    return "%s%s" % (base_url, settings.AVATAR_DEFAULT_URL)


def get_primary_avatar(user, width=settings.AVATAR_DEFAULT_SIZE, height=None):
    User = get_user_model()
    if not isinstance(user, User):
        try:
            user = get_user(user)
        except User.DoesNotExist:
            return None
    try:
        # Order by -primary first; this means if a primary=True avatar exists
        # it will be first, and then ordered by date uploaded, otherwise a
        # primary=False avatar will be first.  Exactly the fallback behavior we
        # want.
        avatar = user.avatar_set.order_by("-primary", "-date_uploaded")[0]
    except IndexError:
        avatar = None
    if avatar:
        if not avatar.thumbnail_exists(width, height):
            avatar.create_thumbnail(width, height)
    return avatar
