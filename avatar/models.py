import datetime
import os

from django.db import models
from django.core.files.base import ContentFile
from django.utils.translation import ugettext as _
from django.utils.hashcompat import md5_constructor
from django.utils.encoding import smart_str
from django.db.models import signals
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

try:
    from cStringIO import StringIO
    dir(StringIO) # Placate PyFlakes
except ImportError:
    from StringIO import StringIO

try:
    from PIL import Image
    dir(Image) # Placate PyFlakes
except ImportError:
    import Image

from avatar.util import invalidate_cache, get_target_handler
from avatar.settings import (AVATAR_STORAGE_DIR, AVATAR_RESIZE_METHOD,
                             AVATAR_MAX_AVATARS_PER_USER, AVATAR_THUMB_FORMAT,
                             AVATAR_HASH_FILENAMES, AVATAR_THUMB_QUALITY,
                             AUTO_GENERATE_AVATAR_SIZES, AVATAR_DEFAULT_SIZE)

def avatar_file_path(instance=None, filename=None, size=None, ext=None):
    handler = get_target_handler()
    tmppath = [AVATAR_STORAGE_DIR]
    tmppath = handler.avatar_file_path(instance, tmppath)
    if not filename:
        # Filename already stored in database
        filename = instance.avatar.name
        if ext and AVATAR_HASH_FILENAMES:
            # An extension was provided, probably because the thumbnail
            # is in a different format than the file. Use it. Because it's
            # only enabled if AVATAR_HASH_FILENAMES is true, we can trust
            # it won't conflict with another filename
            (root, oldext) = os.path.splitext(filename)
            filename = root + "." + ext
    else:
        # File doesn't exist yet
        if AVATAR_HASH_FILENAMES:
            (root, ext) = os.path.splitext(filename)
            filename = md5_constructor(smart_str(filename)).hexdigest()
            filename = filename + ext
    if size:
        tmppath.extend(['resized', str(size)])
    tmppath.append(os.path.basename(filename))
    return os.path.join(*tmppath)

def find_extension(file_format):
    file_format = file_format.lower()

    if file_format == 'jpeg':
        file_format = 'jpg'

    return file_format

class AvatarManager(models.Manager):
    def avatars_for_object(self, obj):
        object_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=object_type.id,
                           object_id=obj.id)

class Avatar(models.Model):
    objects = AvatarManager()

    primary = models.BooleanField(default=False)
    avatar = models.ImageField(max_length=1024, upload_to=avatar_file_path,
                               blank=True)
    date_uploaded = models.DateTimeField(default=datetime.datetime.now)

    #Let avatars attach to any model, not just User(e.g. Team, Group, Moderator)
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return _(u'Avatar for %s: %s') % (unicode(self.content_type),
                                          unicode(self.content_object))

    def save(self, *args, **kwargs):
        avatars = Avatar.objects.avatars_for_object(self.content_object)
        if self.pk:
            avatars = avatars.exclude(pk=self.pk)
        if AVATAR_MAX_AVATARS_PER_USER > 1:
            if self.primary:
                avatars = avatars.filter(primary=True)
                avatars.update(primary=False)
        else:
            avatars.delete()
        invalidate_cache(self.content_object)
        super(Avatar, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        invalidate_cache(self.content_object)
        super(Avatar, self).delete(*args, **kwargs)

    def thumbnail_exists(self, size):
        return self.avatar.storage.exists(self.avatar_name(size))

    def create_thumbnail(self, size, quality=None):
        # invalidate the cache of the thumbnail with the given size first
        invalidate_cache(self.content_object, size)
        try:
            orig = self.avatar.storage.open(self.avatar.name, 'rb').read()
            image = Image.open(StringIO(orig))
        except IOError:
            return # What should we do here?  Render a "sorry, didn't work" img?
        quality = quality or AVATAR_THUMB_QUALITY
        (w, h) = image.size
        if w != size or h != size:
            if w > h:
                diff = (w - h) / 2
                image = image.crop((diff, 0, w - diff, h))
            else:
                diff = (h - w) / 2
                image = image.crop((0, diff, w, h - diff))
            if image.mode != "RGB":
                image = image.convert("RGB")
            image = image.resize((size, size), AVATAR_RESIZE_METHOD)
            thumb = StringIO()
            image.save(thumb, AVATAR_THUMB_FORMAT, quality=quality)
            thumb_file = ContentFile(thumb.getvalue())
        else:
            thumb_file = ContentFile(orig)
        thumb = self.avatar.storage.save(self.avatar_name(size), thumb_file)

    def avatar_url(self, size):
        return self.avatar.storage.url(self.avatar_name(size))

    def url(self):
        return self.avatar_url(AVATAR_DEFAULT_SIZE)

    def avatar_name(self, size):
        ext = find_extension(AVATAR_THUMB_FORMAT)
        return avatar_file_path(
            instance=self,
            size=size,
            ext=ext
        )

def create_default_thumbnails(instance=None, created=False, **kwargs):
    if created:
        for size in AUTO_GENERATE_AVATAR_SIZES:
            instance.create_thumbnail(size)

signals.post_save.connect(create_default_thumbnails, sender=Avatar)
