from django.conf import settings
from PIL import Image

from appconf import AppConf


class AvatarConf(AppConf):
    DEFAULT_SIZE = 80
    RESIZE_METHOD = Image.ANTIALIAS
    STORAGE_DIR = 'avatars'
    GRAVATAR_BASE_URL = 'http://www.gravatar.com/avatar/'
    GRAVATAR_BACKUP = True
    GRAVATAR_DEFAULT = None
    DEFAULT_URL = 'avatar/img/default.jpg'
    MAX_AVATARS_PER_USER = 42
    MAX_SIZE = 1024 * 1024
    THUMB_FORMAT = 'JPEG'
    THUMB_QUALITY = 85
    HASH_FILENAMES = False
    HASH_USERDIRNAMES = False
    ALLOWED_FILE_EXTS = None
    CACHE_TIMEOUT = 60 * 60
    STORAGE = settings.DEFAULT_FILE_STORAGE
    CLEANUP_DELETED = False
    AUTO_GENERATE_SIZES = (DEFAULT_SIZE,)

    def configure_auto_generate_avatar_sizes(self, value):
        return value or getattr(settings, 'AUTO_GENERATE_AVATAR_SIZES',
                                (self.DEFAULT_SIZE,))
