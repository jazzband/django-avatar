from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from avatar.models import Avatar
from avatar.templatetags.avatar_tags import avatar
from avatar.signals import avatar_updated
from avatar.util import User


class AvatarAdmin(admin.ModelAdmin):
    list_display = ('get_avatar', 'user', 'primary', "date_uploaded")
    list_filter = ('primary',)
    search_fields = ('user__%s' % getattr(User, 'USERNAME_FIELD', 'username'),)
    list_per_page = 50

    def get_avatar(self, avatar_in):
        return avatar(avatar_in.user, 80)

    get_avatar.short_description = _('Avatar')
    get_avatar.allow_tags = True

    def save_model(self, request, obj, form, change):
        super(AvatarAdmin, self).save_model(request, obj, form, change)
        avatar_updated.send(sender=Avatar, user=request.user, avatar=obj)


admin.site.register(Avatar, AvatarAdmin)
