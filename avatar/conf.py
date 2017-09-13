from django.conf import settings
from PIL import Image

from appconf import AppConf


class AvatarConf(AppConf):
    DEFAULT_SIZE = 80
    RESIZE_METHOD = Image.ANTIALIAS
    STORAGE_DIR = 'avatars'
    PATH_HANDLER = 'avatar.models.avatar_path_handler'
    GRAVATAR_BASE_URL = 'https://www.gravatar.com/avatar/'
    GRAVATAR_FIELD = 'email'
    GRAVATAR_DEFAULT = None
    AVATAR_GRAVATAR_FORCEDEFAULT = False
    DEFAULT_URL = 'avatar/img/default.jpg'
    MAX_AVATARS_PER_USER = 42
    MAX_SIZE = 1024 * 1024
    THUMB_FORMAT = 'JPEG'
    THUMB_QUALITY = 85
    HASH_FILENAMES = False
    HASH_USERDIRNAMES = False
    EXPOSE_USERNAMES = True
    ALLOWED_FILE_EXTS = None
    CACHE_TIMEOUT = 60 * 60
    STORAGE = settings.DEFAULT_FILE_STORAGE
    CLEANUP_DELETED = False
    AUTO_GENERATE_SIZES = (DEFAULT_SIZE,)
    FACEBOOK_GET_ID = None
    CACHE_ENABLED = True
    RANDOMIZE_HASHES = False
    ADD_TEMPLATE = ''
    CHANGE_TEMPLATE = ''
    DELETE_TEMPLATE = ''
    PROVIDERS = (
        'avatar.providers.PrimaryAvatarProvider',
        'avatar.providers.GravatarAvatarProvider',
        'avatar.providers.DefaultAvatarProvider',
    )

    def configure_auto_generate_avatar_sizes(self, value):
        return value or getattr(settings, 'AVATAR_AUTO_GENERATE_SIZES',
                                (self.DEFAULT_SIZE,))
