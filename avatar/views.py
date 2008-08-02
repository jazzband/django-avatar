import os
import os.path
import tempfile
try:
    from PIL import ImageFile
except ImportError:
    import ImageFile
try:
    from PIL import Image
except ImportError:
    import Image
import shutil

from models import Avatar
from urllib2 import urlopen
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

MAX_MEGABYTES = getattr(settings, 'AVATAR_MAX_FILESIZE', 10)
MAX_WIDTH = getattr(settings, 'AVATAR_MAX_WIDTH', 512)
DEFAULT_WIDTH = getattr(settings, 'AVATAR_DEFAULT_WIDTH', 80)

def _get_next(request):
    """
    The part that's the least straightforward about views in this module is how they 
    determine their redirects after they have finished computation.

    In short, they will try and determine the next place to go in the following order:

    1. If there is a variable named ``next`` in the *POST* parameters, the view will
    redirect to that variable's value.
    2. If there is a variable named ``next`` in the *GET* parameters, the view will
    redirect to that variable's value.
    3. If Django can determine the previous page from the HTTP headers, the view will
    redirect to that previous page.
    4. Otherwise, the view raise a 404 Not Found.
    """
    next = request.POST.get('next', request.GET.get('next', request.META.get('HTTP_REFERER', None)))
    if not next or next == request.path:
        raise Http404 # No next url was supplied in GET or POST.
    return next

def img(request, email_hash, resize_method=Image.ANTIALIAS):
    if email_hash.endswith('.jpg'):
        email_hash = email_hash[:-4]
    try:
        size = int(request.GET.get('s', DEFAULT_WIDTH))
    except ValueError:
        size = DEFAULT_WIDTH
    if size > MAX_WIDTH:
        size = MAX_WIDTH
    rating = request.GET.get('r', 'g') # Unused, for now.
    default = request.GET.get('d', '')
    data = None
    avatar = Avatar.objects.get(email_hash=email_hash)
    try:
        data = open(avatar.get_avatar_filename(), 'r').read()
    except IOError:
        pass 
    if not data and default:
        try:
            data = urlopen(default).read()
        except: #TODO: Fix this hardcore
            pass
    if not data:
        filename = os.path.join(os.path.dirname(__file__), 'default.jpg')
        data = open(filename, 'r').read()
    p = ImageFile.Parser()
    p.feed(data)
    try:
        image = p.close()
    except IOError:
        filename = os.path.join(os.path.dirname(__file__), 'default.jpg')
        try:
            return HttpResponse(open(filename, 'r').read(), mimetype='image/jpeg')
        except: #TODO: Fix this hardcore
            # Is this the right response after so many other things have failed?
            raise Http404
    (width, height) = image.size
    if width > height:
        diff = (width - height) / 2
        image = image.crop((diff, 0, width - diff, height))
    else:
        diff = (height - width) / 2
        image = image.crop((0, diff, width, height - diff))
    image = image.resize((size, size), resize_method)
    response = HttpResponse(mimetype='image/jpeg')
    image.save(response, "JPEG")
    return response

def change(request, extra_context={}, next_override=None):
    if request.method == "POST":
        dirname = os.path.join(settings.MEDIA_ROOT, 'avatars')
        try:
            os.makedirs(dirname)
        except OSError:
            pass # The dirs already exist.
        filename = "%s.jpg" % request.user.avatar.email_hash
        full_filename = os.path.join(dirname, filename)
        (destination, destination_path) = tempfile.mkstemp()
        for i, chunk in enumerate(request.FILES['avatar'].chunks()):
            if i * 16 == MAX_MEGABYTES:
                raise Http404
            os.write(destination, chunk)
        os.close(destination)
        shutil.move(destination_path, full_filename)
        request.user.avatar.avatar = full_filename
        request.user.avatar.save()
        request.user.message_set.create(
            message=_("Successfully updated your avatar."))
        return HttpResponseRedirect(next_override or _get_next(request))
    return render_to_response(
        'avatar/change.html',
        extra_context,
        context_instance = RequestContext(
            request,
            { 'avatar': request.user.avatar, 
              'next': next_override or _get_next(request) }
        )
    )
change = login_required(change)

def delete(request, extra_context={}, next_override=None):
    if request.method == 'POST':
        # Should we really delete a OneToOneField?
        # I think just set image to default.
        # request.user.avatar.delete()
        request.user.avatar.avatar = "DEFAULT"
        request.user.avatar.save()
        request.user.message_set.create(
            message=_("Successfully removed your avatar."))
        next = next_override or _get_next(request)
        return HttpResponseRedirect(next)
    return render_to_response(
        'avatar/confirm_delete.html',
        extra_context,
        context_instance = RequestContext(
            request,
            { 'avatar': request.user.avatar,
              'next': next_override or _get_next(request) }
        )
    )
delete = login_required(delete)