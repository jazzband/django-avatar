from appconf import AppConf


class AvatarAPIConf(AppConf):
    # allow updating avatar image in put method
    AVATAR_CHANGE_IMAGE = False
