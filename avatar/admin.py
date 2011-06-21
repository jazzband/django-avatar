from django.contrib import admin
from avatar.models import Avatar
from templatetags.avatar_tags import avatar

class AvatarAdmin(admin.ModelAdmin):
    list_display        = ('get_avatar', 'user', 'primary', "date_uploaded")
    list_filter         = ('primary',)
    search_fields       = ('user__username',)
    list_per_page       = 50
    
    def get_avatar(self, avatar_in):
        return avatar(avatar_in.user, 80)
        
    get_avatar.short_description = 'Avatar'
    get_avatar.allow_tags = True


admin.site.register(Avatar, AvatarAdmin)