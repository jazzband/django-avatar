from django.contrib.auth.models import User
from models import Avatar
from django.db.models import signals

def create_avatar(sender=None, instance=None, **kwargs):
    avatar, created = Avatar.objects.get_or_create(user=instance)
    avatar.save()
def delete_avatar(sender=None, instance=None, **kwargs):
    try:
        Avatar.objects.get(user=instance).delete()
    except Avatar.DoesNotExist:
        pass
signals.post_save.connect(create_avatar, sender=User)
signals.post_delete.connect(delete_avatar, sender=User)
