from django.contrib.auth.models import User
from django.utils.hashcompat import md5_constructor

from avatar.models import Avatar
from avatar.settings import AVATAR_HASH_USERDIRNAMES

class DefaultTargetHandler(object):
    """
    Default avatar target handler that expects to operate on django user objects
    """

    def get_gravatar_url(self, user_or_username):
        user = self.get_user(user_or_username)
        if not user:
            return None
        return user.email

    def get_user(self, user_or_username):
        if not isinstance(user_or_username, User):
            try:
                return User.objects.get(username=user_or_username)
            except User.DoesNotExist:
                return None
        return user_or_username

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
        if not isinstance(user, User):
            try:
                user = User.objects.get(username=user)
            except User.DoesNotExist:
                return None
        return user

    def get_target_from_type(self, target_type, target_id):
        return self.get_target_object(target_id)

    def get_alt_text(self, user):
        return unicode(user)

    def get_type(self, user):
        return "user"

    def get_id(self, user):
        return user.id

    def new_avatar(self, user, image_file):
        avatar = Avatar(
                content_object=user,
                primary=True,
            )
        avatar.avatar.save(image_file.name, image_file)
        avatar.save()
        return avatar

    def get_avatar(self, user, user_id):
        return Avatar.objects.get(id=user_id)

    def add_template(self, is_ajax=False):
        return 'avatar/add.html'

    def change_template(self, is_ajax=False):
        return 'avatar/change.html'

    def delete_template(self, is_ajax=False):
        return 'avatar/confirm_delete.html'

    def avatar_file_path(self, instance, tmppath):
        if AVATAR_HASH_USERDIRNAMES:
            tmp = md5_constructor(instance.content_object.username).hexdigest()
            tmppath.extend([tmp[0], tmp[1], instance.content_object.username])
        else:
            tmppath.append(instance.content_object.username)
        return tmppath

    def get_upload_form(self):
        return None

    def get_primary_form(self):
        return None

    def get_delete_form(self):
        return None
