from django.conf import settings

from django.contrib.auth.models import User

from avatar import AVATAR_DEFAULT_URL

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

def get_primary_avatar(user, size=80):
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
