from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from avatar.models import Avatar
from avatar.templatetags.avatar_tags import avatar_choice_url
from avatar.util import User

class AvatarAdmin(admin.ModelAdmin):
    list_display = ('get_avatar', 'user', 'primary', "date_uploaded")
    list_filter = ('primary',)
    search_fields = ('user__%s' % getattr(User, 'USERNAME_FIELD', 'username'),)
    list_per_page = 50

    def get_avatar(self, avatar):
        size = 80
        url = avatar_choice_url(avatar, size)
        return """<img src="%s" alt="%s" width="%s" height="%s" />""" % (
        url, str(avatar), size, size)

    get_avatar.short_description = _('Avatar')
    get_avatar.allow_tags = True

admin.site.register(Avatar, AvatarAdmin)
