import os

from avatar.api.shortcut import get_object_or_none
from avatar.conf import settings
from avatar.models import Avatar, invalidate_avatar_cache


def create_default_thumbnails(sender, instance, created=False, **kwargs):
    invalidate_avatar_cache(sender, instance)

    if not created:
        for size in settings.AVATAR_AUTO_GENERATE_SIZES:
            if isinstance(size, int):
                if not instance.thumbnail_exists(size, size):
                    instance.create_thumbnail(size, size)
            else:
                # Size is specified with height and width.
                if not instance.thumbnail_exists(size[0, size[0]]):
                    instance.create_thumbnail(size[0], size[1])


def remove_previous_avatar_images_when_update(
    sender, instance=None, created=False, update_main_avatar=True, **kwargs
):
    if not created:
        old_instance = get_object_or_none(Avatar, pk=instance.pk)
        if old_instance and not old_instance.avatar == instance.avatar:
            base_filepath = old_instance.avatar.name
            path, filename = os.path.split(base_filepath)
            # iterate through resized avatars directories and delete resized avatars
            resized_path = os.path.join(path, "resized")
            try:
                resized_widths, _ = old_instance.avatar.storage.listdir(resized_path)
                for width in resized_widths:
                    resized_width_path = os.path.join(resized_path, width)
                    resized_heights, _ = old_instance.avatar.storage.listdir(
                        resized_width_path
                    )
                    for height in resized_heights:
                        if old_instance.thumbnail_exists(width, height):
                            old_instance.avatar.storage.delete(
                                old_instance.avatar_name(width, height)
                            )
                if update_main_avatar:
                    if old_instance.avatar.storage.exists(old_instance.avatar.name):
                        old_instance.avatar.storage.delete(old_instance.avatar.name)
            except FileNotFoundError:
                pass
