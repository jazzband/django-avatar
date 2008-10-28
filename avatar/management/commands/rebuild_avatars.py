from django.core.management.base import NoArgsCommand
from django.conf import settings

from avatar.models import Avatar
from avatar import AUTO_GENERATE_AVATAR_SIZES

class Command(NoArgsCommand):
    help = "Regenerates avatar thumbnails for the sizes specified in " + \
        "settings.AUTO_GENERATE_AVATAR_SIZES."
    
    def handle_noargs(self, **options):
        for avatar in Avatar.objects.all():
            for size in AUTO_GENERATE_AVATAR_SIZES:
                print "Rebuilding Avatar id=%s at size %s." % (avatar.id, size)
                avatar.create_thumbnail(size)