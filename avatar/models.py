import datetime
import os
import hashlib
from PIL import Image

from django.db import models
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.storage import get_storage_class
from django.utils.translation import ugettext as _
from django.utils import six
from django.db.models import signals

from avatar.conf import settings
from avatar.util import get_username, force_bytes, invalidate_cache

try:
    from django.utils.timezone import now
except ImportError:
    now = datetime.datetime.now


avatar_storage = get_storage_class(settings.AVATAR_STORAGE)()


def avatar_file_path(instance=None, filename=None, size=None, ext=None):
    tmppath = [settings.AVATAR_STORAGE_DIR]
    userdirname = get_username(instance.user)
    if settings.AVATAR_USERID_AS_USERDIRNAME:
        userdirname = str(instance.user_id)
    if settings.AVATAR_HASH_USERDIRNAMES:
        tmp = hashlib.md5(userdirname).hexdigest()
        tmppath.extend([tmp[0], tmp[1], userdirname])
    else:
        tmppath.append(userdirname)
    if not filename:
        # Filename already stored in database
        filename = instance.avatar.name
        if ext and settings.AVATAR_HASH_FILENAMES:
            # An extension was provided, probably because the thumbnail
            # is in a different format than the file. Use it. Because it's
            # only enabled if AVATAR_HASH_FILENAMES is true, we can trust
            # it won't conflict with another filename
            (root, oldext) = os.path.splitext(filename)
            filename = root + "." + ext
    else:
        # File doesn't exist yet
        if settings.AVATAR_HASH_FILENAMES:
            (root, ext) = os.path.splitext(filename)
            filename = hashlib.md5(force_bytes(filename)).hexdigest()
            filename = filename + ext
    if size:
        tmppath.extend(['resized', str(size)])
    tmppath.append(os.path.basename(filename))
    return os.path.join(*tmppath)


def find_extension(format):
    format = format.lower()

    if format == 'jpeg':
        format = 'jpg'

    return format


class Avatar(models.Model):
    user = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'))
    primary = models.BooleanField(default=False)
    avatar = models.ImageField(max_length=1024,
                               upload_to=avatar_file_path,
                               storage=avatar_storage,
                               blank=True)
    date_uploaded = models.DateTimeField(default=now)

    def __unicode__(self):
        return _(six.u('Avatar for %s')) % self.user

    def save(self, *args, **kwargs):
        avatars = Avatar.objects.filter(user=self.user)
        if self.pk:
            avatars = avatars.exclude(pk=self.pk)
        if settings.AVATAR_MAX_AVATARS_PER_USER > 1:
            if self.primary:
                avatars = avatars.filter(primary=True)
                avatars.update(primary=False)
        else:
            avatars.delete()
        super(Avatar, self).save(*args, **kwargs)

    def thumbnail_exists(self, size):
        return self.avatar.storage.exists(self.avatar_name(size))

    def transpose_image(self, image):
        """
            Transpose based on EXIF information.
            Borrowed from django-imagekit:
            imagekit.processors.Transpose
        """
        EXIF_ORIENTATION_STEPS = {
            1: [],
            2: ['FLIP_LEFT_RIGHT'],
            3: ['ROTATE_180'],
            4: ['FLIP_TOP_BOTTOM'],
            5: ['ROTATE_270', 'FLIP_LEFT_RIGHT'],
            6: ['ROTATE_270'],
            7: ['ROTATE_90', 'FLIP_LEFT_RIGHT'],
            8: ['ROTATE_90'],
        }
        try:
            orientation = image._getexif()[0x0112]
            ops = EXIF_ORIENTATION_STEPS[orientation]
        except:
            ops = []
        for method in ops:
            image = image.transpose(getattr(Image, method))
        return image

    def create_thumbnail(self, size, quality=None):
        # invalidate the cache of the thumbnail with the given size first
        invalidate_cache(self.user, size)
        try:
            orig = self.avatar.storage.open(self.avatar.name, 'rb')
            image = Image.open(orig)
            image = self.transpose_image(image)
            quality = quality or settings.AVATAR_THUMB_QUALITY
            w, h = image.size
            if w != size or h != size:
                if w > h:
                    diff = int((w - h) / 2)
                    image = image.crop((diff, 0, w - diff, h))
                else:
                    diff = int((h - w) / 2)
                    image = image.crop((0, diff, w, h - diff))
                if image.mode not in ("RGB", "RGBA"):
                    image = image.convert("RGB")
                image = image.resize((size, size), settings.AVATAR_RESIZE_METHOD)
                thumb = six.BytesIO()
                image.save(thumb, settings.AVATAR_THUMB_FORMAT, quality=quality)
                thumb_file = ContentFile(thumb.getvalue())
            else:
                thumb_file = File(orig)
            thumb = self.avatar.storage.save(self.avatar_name(size), thumb_file)
        except IOError:
            return  # What should we do here?  Render a "sorry, didn't work" img?

    def avatar_url(self, size):
        return self.avatar.storage.url(self.avatar_name(size))

    def get_absolute_url(self):
        return self.avatar_url(settings.AVATAR_DEFAULT_SIZE)

    def avatar_name(self, size):
        ext = find_extension(settings.AVATAR_THUMB_FORMAT)
        return avatar_file_path(
            instance=self,
            size=size,
            ext=ext
        )


def invalidate_avatar_cache(sender, instance, **kwargs):
    if hasattr(instance, 'user'):
        invalidate_cache(instance.user)


def create_default_thumbnails(sender, instance, created=False, **kwargs):
    invalidate_avatar_cache(sender, instance)
    if created:
        for size in settings.AVATAR_AUTO_GENERATE_SIZES:
            instance.create_thumbnail(size)


def remove_avatar_images(instance=None, **kwargs):
    if hasattr(instance, 'user'):
        for size in settings.AVATAR_AUTO_GENERATE_SIZES:
            if instance.thumbnail_exists(size):
                instance.avatar.storage.delete(instance.avatar_name(size))
        instance.avatar.storage.delete(instance.avatar.name)


signals.post_save.connect(create_default_thumbnails, sender=Avatar)
signals.post_delete.connect(invalidate_avatar_cache, sender=Avatar)

if settings.AVATAR_CLEANUP_DELETED:
    signals.post_delete.connect(remove_avatar_images, sender=Avatar)
