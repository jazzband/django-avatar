from django.conf import settings
from django.db.models import signals
from django.utils.translation import ugettext_noop as _

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
    
    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("avatar_updated", _("Avatar Updated"), _("avatar have been updated"))
        notification.create_notice_type("avatar_friend_updated", _("Friend Updated Avatar"), _("a friend has updated his avatar"))
    
    signals.post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes as notification app not found"
