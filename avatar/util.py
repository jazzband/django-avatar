from django.conf import settings
from django.core.cache import cache

from django.contrib.auth.models import User

from avatar.settings import (AVATAR_DEFAULT_URL, AVATAR_CACHE_TIMEOUT,
                             AUTO_GENERATE_AVATAR_SIZES, AVATAR_DEFAULT_SIZE)

cached_funcs = set()

def get_cache_key(user_or_username, size, prefix):
    """
    Returns a cache key consisten of a username and image size.
    """
    if isinstance(user_or_username, User):
        user_or_username = user_or_username.username
    return '%s_%s_%s' % (prefix, user_or_username, size)

def cache_result(func):
    """
    Decorator to cache the result of functions that take a ``user`` and a
    ``size`` value.
    """
    def cache_set(key, value):
        cache.set(key, value, AVATAR_CACHE_TIMEOUT)
        return value

    def cached_func(user, size):
        prefix = func.__name__
        cached_funcs.add(prefix)
        key = get_cache_key(user, size, prefix=prefix)
        return cache.get(key) or cache_set(key, func(user, size))
    return cached_func

def invalidate_cache(user, size=None):
    """
    Function to be called when saving or changing an user's avatars.
    """
    sizes = set(AUTO_GENERATE_AVATAR_SIZES)
    if size is not None:
        sizes.add(size)
    for prefix in cached_funcs:
        for size in sizes:
            cache.delete(get_cache_key(user, size, prefix))

def get_default_avatar_url():
    base_url = getattr(settings, 'STATIC_URL', None)
    if not base_url:
        base_url = getattr(settings, 'MEDIA_URL', '')
    # Don't use base_url if the default avatar url starts with http:// of https://
    if AVATAR_DEFAULT_URL.startswith('http://') or AVATAR_DEFAULT_URL.startswith('https://'):
        return AVATAR_DEFAULT_URL
    # We'll be nice and make sure there are no duplicated forward slashes
    ends = base_url.endswith('/')
    begins = AVATAR_DEFAULT_URL.startswith('/')
    if ends and begins:
        base_url = base_url[:-1]
    elif not ends and not begins:
        return '%s/%s' % (base_url, AVATAR_DEFAULT_URL)
    return '%s%s' % (base_url, AVATAR_DEFAULT_URL)

def get_primary_avatar(user, size=AVATAR_DEFAULT_SIZE):
    if not isinstance(user, User):
        try:
            user = User.objects.get(username=user)
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
        if not avatar.thumbnail_exists(size):
            avatar.create_thumbnail(size)
    return avatar
