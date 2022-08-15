from django.core.management.base import BaseCommand

from avatar.conf import settings
from avatar.models import Avatar, remove_avatar_images


class Command(BaseCommand):
    help = (
        "Regenerates avatar thumbnails for the sizes specified in "
        "settings.AVATAR_AUTO_GENERATE_SIZES."
    )

    def handle(self, *args, **options):
        for avatar in Avatar.objects.all():
            if settings.AVATAR_CLEANUP_DELETED:
                remove_avatar_images(avatar, delete_main_avatar=False)
            for size in settings.AVATAR_AUTO_GENERATE_SIZES:
                if options["verbosity"] != 0:
                    self.stdout.write(
                        "Rebuilding Avatar id=%s at size %s." % (avatar.id, size)
                    )
                if isinstance(size, int):
                    avatar.create_thumbnail(size, size)
                else:
                    # Size is specified with height and width.
                    avatar.create_thumbnail(size[0], size[1])
