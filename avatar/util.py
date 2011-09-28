from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.contrib.auth.models import User
from django.utils.hashcompat import md5_constructor

from avatar.settings import (AVATAR_DEFAULT_URL, AVATAR_CACHE_TIMEOUT,
                             AUTO_GENERATE_AVATAR_SIZES, AVATAR_DEFAULT_SIZE,
                             AVATAR_TARGET_HANDLER, AVATAR_HASH_USERDIRNAMES)
import avatar as av

cached_funcs = set()

def get_target_handler(path=AVATAR_TARGET_HANDLER):
    """
    Return an instance of a target handler, given the dotted
    Python import path (as a string) to the handler class.

    If the handler cannot be located (e.g., because no such module
    exists, or because the module does not contain a class of the
    appropriate name), ``django.core.exceptions.ImproperlyConfigured``
    is raised.
    """

    i = path.rfind('.')
    module, attr = path[:i], path[i + 1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error loading target handler %s: "%s"' % (module, e))
    try:
        backend_class = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a target handler named "%s"' % (module, attr))
    return backend_class()

def get_cache_key(target, size, prefix):
    """
    Returns a cache key consisting of a target-specific key and image size.
    """
    handler = get_target_handler()
    key = handler.get_cache_key(target)
    return '%s_%s_%s' % (prefix, key, size)

def cache_result(func):
    """
    Decorator to cache the result of functions that take a ``target`` and a
    ``size`` value.
    """
    def cache_set(key, value):
        cache.set(key, value, AVATAR_CACHE_TIMEOUT)
        return value

    def cached_func(target, size):
        prefix = func.__name__
        cached_funcs.add(prefix)
        key = get_cache_key(target, size, prefix=prefix)
        return cache.get(key) or cache_set(key, func(target, size))
    return cached_func

def invalidate_cache(target, size=None):
    """
    Function to be called when saving or changing a target's avatars.
    """
    sizes = set(AUTO_GENERATE_AVATAR_SIZES)
    if size is not None:
        sizes.add(size)
    for prefix in cached_funcs:
        for size in sizes:
            cache.delete(get_cache_key(target, size, prefix))

def get_default_avatar_url(target, size=None):
    base_url = getattr(settings, 'STATIC_URL', None)
    if not base_url:
        base_url = getattr(settings, 'MEDIA_URL', '')

    handler = get_target_handler()
    return handler.get_default_avatar_url(target, base_url, AVATAR_DEFAULT_URL, size)

def get_primary_avatar(target, size=AVATAR_DEFAULT_SIZE):
    handler = get_target_handler()
    obj = handler.get_target_object(target)
    if not obj:
        return None
    try:
        # Order by -primary first; this means if a primary=True avatar exists
        # it will be first, and then ordered by date uploaded, otherwise a
        # primary=False avatar will be first.  Exactly the fallback behavior we
        # want.
        avatar = av.models.Avatar.objects.avatars_for_object(obj).order_by("-primary", "-date_uploaded")[0]
    except IndexError:
        avatar = None
    if avatar:
        if not avatar.thumbnail_exists(size):
            avatar.create_thumbnail(size)
    return avatar

def get_target_gravatar_url(target):
    """
    Return the string to be used for creating the gravatar url for the target object
    """
    handler = get_target_handler()
    return handler.get_gravatar_url(target)

def get_user(user_or_username):
    if not isinstance(user_or_username, User):
        try:
            return User.objects.get(username=user_or_username)
        except User.DoesNotExist:
            return None
    return user_or_username

class DefaultTargetHandler(object):
    """
    Default avatar target handler that expects to operate on django user objects
    """
    def get_gravatar_url(self, user_or_username):
        user = get_user(user_or_username)
        if not user:
            return None
        return user.email

    def get_cache_key(self, user_or_username):
        if isinstance(user_or_username, User):
            user_or_username = user_or_username.username
        return user_or_username

    def get_default_avatar_url(self, user_or_username, base_url, default_url,
                               size=None):
        # Don't use base_url if the default avatar url starts with http[s]://
        if default_url.startswith('http://') or \
            default_url.startswith('https://'):
            return default_url
        # We'll be nice and make sure there are no duplicated forward slashes
        ends = base_url.endswith('/')
        begins = default_url.startswith('/')
        if ends and begins:
            base_url = base_url[:-1]
        elif not ends and not begins:
            return '%s/%s' % (base_url, default_url)
        return '%s%s' % (base_url, default_url)

    def get_target_object(self, user):
        return get_user(user)

    def get_alt_text(self, user):
        return unicode(user)

    def get_primary_avatar_kwargs(self, target):
        return {'user': target.username }

    def avatar_file_path(self, instance, tmppath):
        if AVATAR_HASH_USERDIRNAMES:
            tmp = md5_constructor(instance.content_object.username).hexdigest()
            tmppath.extend([tmp[0], tmp[1], instance.content_object.username])
        else:
            tmppath.append(instance.content_object.username)
        return tmppath
