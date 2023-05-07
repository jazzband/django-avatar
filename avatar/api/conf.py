from appconf import AppConf
from django.conf import settings


class AvatarAPIConf(AppConf):
    # allow updating avatar image in put method
    AVATAR_CHANGE_IMAGE = False
