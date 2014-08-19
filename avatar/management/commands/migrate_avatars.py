import os
import shutil
from django.core.management import call_command
from django.core.management.base import NoArgsCommand
from avatar.conf import settings
from avatar.models import Avatar, avatar_file_path
from django.core.files import File


class Command(NoArgsCommand):
    help = ("Check if avatar userdirname folder correspond "
            "with actual userdirname pattern "
            "affect with options like AVATAR_USERID_AS_USERDIRNAME "
            "or AVATAR_HASH_USERDIRNAMES.")

    def handle_noargs(self, **options):
        # define path to avatar folders
        avatar_path = os.path.join(settings.MEDIA_URL,
                                   settings.AVATAR_STORAGE_DIR)

        have_change = False
        for avatar in Avatar.objects.all():
            # get actuel path of avatar
            new_path = os.path.join(settings.MEDIA_URL,
                                    avatar_file_path(avatar))
            original_path = avatar.avatar.url
            if new_path != original_path:
                print("Move Avatar id=%s from %s to %s." % (avatar.id,
                                                            original_path,
                                                            new_path))

                # if different path: we copy + generate new thumbnails + clean
                media_path = original_path.replace(settings.MEDIA_URL, "")
                media_path = os.path.join(settings.MEDIA_ROOT, media_path)
                # copy original avatar into new folder
                avatar.avatar.save(os.path.basename(new_path),
                                   File(open(media_path)))
                avatar.save()

                # delete old folder and thumbnails
                i = original_path.find('/', len(avatar_path) + 1)
                folder = original_path[0:i]
                if folder[0:1] == "/":
                    folder = folder[1:]
                folder = os.path.join(settings.BASE_DIR, folder)
                print("Delete useless folder %s" % folder)
                shutil.rmtree(folder)
                have_change = True

        # generate all default thumbnails in new folder
        if have_change:
            call_command('rebuild_avatars')
        else:
            print("No change ;)")
