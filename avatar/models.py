import os.path

from django.db import models
from django.contrib.auth.models import User

try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5

RATING_CHOICES = (
    ('g', 'G'),
    ('pg', 'PG'),
    ('r', 'R'),
    ('x', 'X'),
)

class Avatar(models.Model):
    email_hash = models.CharField(max_length=128, blank=True)
    user = models.OneToOneField(User)
    # This should have a subdirectory of each user's avatar, but first we need
    # patch #5361 to land into Trunk.
    avatar = models.FileField(upload_to='avatars/', default='DEFAULT')
    rating = models.CharField(choices=RATING_CHOICES, max_length=2, default='g')
    
    def __unicode__(self):
        return u'Gravatar for %s' % self.user
    
    def save(self):
        self.email_hash = md5(self.user.email).hexdigest().lower()
        super(Avatar, self).save()