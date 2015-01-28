from django.conf import settings

def default_avatar_admin_test(request, target_user):
    # A callback function for testing whether the user making the request
    # has permission to manage the target user's avatars. By default,
    # nobody has this permission.
    return False

AVATAR_ADMIN_TEST = getattr(
    settings,
    'AVATAR_ADMIN_TEST',
    default_avatar_admin_test,
)
