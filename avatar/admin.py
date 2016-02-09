from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.utils import six
from django.template.loader import render_to_string

from avatar.models import Avatar
from avatar.signals import avatar_updated
from avatar.utils import get_user_model


class AvatarAdmin(admin.ModelAdmin):
    list_display = ('get_avatar', 'user', 'primary', "date_uploaded")
    list_filter = ('primary',)
    search_fields = ('user__%s' % getattr(get_user_model(), 'USERNAME_FIELD', 'username'),)
    list_per_page = 50

    def get_avatar(self, avatar_in):
        context = dict({
            'user': avatar_in.user,
            'url': avatar_in.avatar.url,
            'alt': six.text_type(avatar_in.user),
            'size': 80,
        })
        return render_to_string('avatar/avatar_tag.html', context)

    get_avatar.short_description = _('Avatar')
    get_avatar.allow_tags = True

    def save_model(self, request, obj, form, change):
        super(AvatarAdmin, self).save_model(request, obj, form, change)
        avatar_updated.send(sender=Avatar, user=request.user, avatar=obj)


admin.site.register(Avatar, AvatarAdmin)
