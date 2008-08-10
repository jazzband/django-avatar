import re
import datetime
import os.path

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.utils.translation import ugettext as _

try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5
try:
    from PIL import ImageFile
except ImportError:
    import ImageFile
try:
    from PIL import Image
except ImportError:
    import Image

WIDTH_HEIGHT_RE = re.compile(r'\[(\d+)x(\d+)\]')

AUTO_GENERATE_AVATAR_SIZES = getattr(settings, 'AUTO_GENERATE_AVATAR_SIZES', (80,))
AVATAR_RESIZE_METHOD = getattr(settings, 'AVATAR_RESIZE_METHOD', Image.ANTIALIAS)

def avatar_file_path(instance=None, filename=None):
    return 'avatars/%s/[%sx%s]%s' % (instance.user.username, 
        instance.avatar.width, instance.avatar.height, filename)

class Avatar(models.Model):
    email_hash = models.CharField(max_length=128, blank=True)
    user = models.ForeignKey(User)
    primary = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to=avatar_file_path, blank=True)
    date_uploaded = models.DateTimeField(default=datetime.datetime.now)
    
    def __unicode__(self):
        return _(u'Avatar for %s' % self.user)
    
    def save(self):
        self.email_hash = md5(self.user.email).hexdigest().lower()
        if self.primary:
            avatars = Avatar.objects.filter(user=self.user, primary=True)
            avatars.update(primary=False)
        super(Avatar, self).save()
    
    def thumbnail_exists(self, size):
        if size in AUTO_GENERATE_AVATAR_SIZES:
            return True
        new_path_fragment = '[%sx%s]' % (size, size)
        path = WIDTH_HEIGHT_RE.sub(new_path_fragment, self.avatar.path)
        return default_storage.exists(path)
    
    def create_thumbnail(self, size):
        orig = default_storage.open(self.avatar.path, 'rb').read()
        p = ImageFile.Parser()
        p.feed(orig)
        try:
            image = p.close()
        except IOError:
            return # What should we do here?  Render a "sorry, didn't work" img?
        (w, h) = image.size
        if w > h:
            diff = (w - h) / 2
            image = image.crop((diff, 0, w - diff, h))
        else:
            diff = (h - w) / 2
            image = image.crop((0, diff, w, h - diff))
        image = image.resize((size, size), AVATAR_RESIZE_METHOD)
        thumb = default_storage.open(self.avatar_path(size), 'wb')
        image.save(thumb, "JPEG")
    
    def avatar_url(self, size):
        new_url_fragment = '[%sx%s]' % (size, size)
        return WIDTH_HEIGHT_RE.sub(new_url_fragment, self.avatar.url)

    def avatar_path(self, size):
        new_path_fragment = '[%sx%s]' % (size, size)
        return WIDTH_HEIGHT_RE.sub(new_path_fragment, self.avatar.path)