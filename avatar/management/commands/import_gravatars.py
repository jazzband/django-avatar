import os
import os.path

from urllib2 import urlopen
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import NoArgsCommand

try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5

def hashify(inp):
    return md5(inp).hexdigest().lower()

class Command(NoArgsCommand):
    help = "Import avatars from Gravatar, and store them locally."
    
    def handle_noargs(self, **options):
        # I'm OK with bare exceptions here, since we want totally graceful and
        # aggressive failure on a massive import like this.
        for user in User.objects.all():
            if user.email:
                url = "http://www.gravatar.com/avatar/%s" % hashify(user.email)
                try:
                    data = urlopen(url).read()
                except:
                    print "Errored on opening URL: %s" % url
                    continue
            else:
                print "%s has no e-mail address specified." % user.username
                continue
            dirname = os.path.join(settings.MEDIA_ROOT, 'avatars')
            try:
                os.makedirs(dirname)
            except OSError:
                pass
            filename = "%s.jpg" % user.avatar.email_hash
            full_filename = os.path.join(dirname, filename)
            try:
                f = open(full_filename, 'w')
                f.write(data)
                f.close()
                user.avatar.avatar = full_filename
                user.avatar.save()
                print "Imported Gravatar for %s" % user.username
            except:
                print "Error on writing to file: %s" % full_filename
                continue
            