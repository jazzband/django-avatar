from django.contrib.auth.models import User
from models import Avatar
from django.dispatch import dispatcher
from django.db.models import signals

def create_avatar(sender, instance):
    avatar, created = Avatar.objects.get_or_create(user=instance)
    avatar.save()
def delete_avatar(sender, instance):
    try:
        Avatar.objects.get(user=instance).delete()
    except Avatar.DoesNotExist:
        pass
dispatcher.connect(create_avatar, sender=User, signal=signals.post_save)
dispatcher.connect(delete_avatar, sender=User, signal=signals.post_delete)
