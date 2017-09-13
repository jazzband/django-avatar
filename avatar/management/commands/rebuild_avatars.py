from django.core.management.base import BaseCommand

from avatar.conf import settings
from avatar.models import Avatar


class Command(BaseCommand):
    help = ("Regenerates avatar thumbnails for the sizes specified in "
            "settings.AVATAR_AUTO_GENERATE_SIZES.")

    def handle(self, *args, **options):
        for avatar in Avatar.objects.all():
            for size in settings.AVATAR_AUTO_GENERATE_SIZES:
                if options['verbosity'] != 0:
                    print("Rebuilding Avatar id=%s at size %s." % (avatar.id, size))

                avatar.create_thumbnail(size)
