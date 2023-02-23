from appconf import AppConf
from django.conf import settings
from PIL import Image
from PIL import __version__ as __pil_version__
from packaging.version import parse, Version

if parse(__pil_version__) > Version('9.1.0'):
    # https://pillow.readthedocs.io/en/stable/deprecations.html#constants
    # https://github.com/jazzband/django-avatar/issues/222
    # Since 9.1.0, Image.ANTIALIAS is deprecated and replaced by Image.Resampling.LANCZOS and Image.LANCZOS
    _RESIZE_METHOD = Image.Resampling.LANCZOS
else:
    _RESIZE_METHOD = Image.ANTIALIAS


class AvatarConf(AppConf):
    DEFAULT_SIZE = 80
    RESIZE_METHOD = _RESIZE_METHOD
    STORAGE_DIR = "avatars"
    PATH_HANDLER = "avatar.models.avatar_path_handler"
    GRAVATAR_BASE_URL = "https://www.gravatar.com/avatar/"
    GRAVATAR_FIELD = "email"
    GRAVATAR_DEFAULT = None
    AVATAR_GRAVATAR_FORCEDEFAULT = False
    DEFAULT_URL = "avatar/img/default.jpg"
    MAX_AVATARS_PER_USER = 42
    MAX_SIZE = 1024 * 1024
    THUMB_FORMAT = "PNG"
    THUMB_QUALITY = 85
    THUMB_MODES = ("RGB", "RGBA")
    HASH_FILENAMES = False
    HASH_USERDIRNAMES = False
    EXPOSE_USERNAMES = False
    ALLOWED_FILE_EXTS = None
    ALLOWED_MIMETYPES = None
    CACHE_TIMEOUT = 60 * 60
    STORAGE = settings.DEFAULT_FILE_STORAGE
    CLEANUP_DELETED = True
    AUTO_GENERATE_SIZES = (DEFAULT_SIZE,)
    FACEBOOK_GET_ID = None
    CACHE_ENABLED = True
    RANDOMIZE_HASHES = False
    ADD_TEMPLATE = ""
    CHANGE_TEMPLATE = ""
    DELETE_TEMPLATE = ""
    PROVIDERS = (
        "avatar.providers.PrimaryAvatarProvider",
        "avatar.providers.LibRAvatarProvider",
        "avatar.providers.GravatarAvatarProvider",
        "avatar.providers.DefaultAvatarProvider",
    )

    def configure_auto_generate_avatar_sizes(self, value):
        return value or getattr(
            settings, "AVATAR_AUTO_GENERATE_SIZES", (self.DEFAULT_SIZE,)
        )
