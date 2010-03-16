import datetime
import os.path

from django.db import models
from django.core.files.base import ContentFile
from django.utils.translation import ugettext as _
from django.utils.hashcompat import md5_constructor
from django.utils.encoding import smart_str

from django.contrib.auth.models import User

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

from avatar import AVATAR_STORAGE_DIR, AVATAR_RESIZE_METHOD, \
                   AVATAR_MAX_AVATARS_PER_USER, AVATAR_THUMB_FORMAT, \
                   AVATAR_HASH_USERDIRNAMES, AVATAR_HASH_FILENAMES, \
                   AVATAR_THUMB_QUALITY

def avatar_file_path(instance=None, filename=None, size=None, ext=None):
    tmppath = [AVATAR_STORAGE_DIR]
    if AVATAR_HASH_USERDIRNAMES:
        tmp = md5_constructor(instance.user.username).hexdigest()
        tmppath.extend([tmp[0], tmp[1], instance.user.username])
    else:
        tmppath.append(instance.user.username)
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

def find_extension(format):
    format = format.lower()

    if format == 'jpeg':
        format = 'jpg'

    return format

class Avatar(models.Model):
    user = models.ForeignKey(User)
    primary = models.BooleanField(default=False)
    avatar = models.ImageField(max_length=1024, upload_to=avatar_file_path, blank=True)
    date_uploaded = models.DateTimeField(default=datetime.datetime.now)
    
    def __unicode__(self):
        return _(u'Avatar for %s') % self.user
    
    def save(self, force_insert=False, force_update=False):
        avatars = Avatar.objects.filter(user=self.user).exclude(id=self.id)
        if AVATAR_MAX_AVATARS_PER_USER > 1:
            if self.primary:
                avatars = avatars.filter(primary=True)
                avatars.update(primary=False)
        else:
            avatars.delete()
        super(Avatar, self).save(force_insert, force_update)
    
    def thumbnail_exists(self, size):
        return self.avatar.storage.exists(self.avatar_name(size))
    
    def create_thumbnail(self, size, quality=None):
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
            image = image.resize((size, size), AVATAR_RESIZE_METHOD)
            if image.mode != "RGB":
                image = image.convert("RGB")
            thumb = StringIO()
            image.save(thumb, AVATAR_THUMB_FORMAT, quality=quality)
            thumb_file = ContentFile(thumb.getvalue())
        else:
            thumb_file = ContentFile(orig)
        thumb = self.avatar.storage.save(self.avatar_name(size), thumb_file)
    
    def avatar_url(self, size):
        return self.avatar.storage.url(self.avatar_name(size))
    
    def avatar_name(self, size):
        ext = find_extension(AVATAR_THUMB_FORMAT)
        return avatar_file_path(
            instance=self,
            size=size,
            ext=ext
        )
