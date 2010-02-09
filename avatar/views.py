import os.path

from avatar.models import Avatar, avatar_file_path
from avatar.forms import PrimaryAvatarForm, DeleteAvatarForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from django.db.models import get_app
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

try:
    notification = get_app('notification')
except ImproperlyConfigured:
    notification = None

friends = False
if 'friends' in settings.INSTALLED_APPS:
    friends = True
    from friends.models import Friendship

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
    """
    next = request.POST.get('next', request.GET.get('next', request.META.get('HTTP_REFERER', None)))
    if not next:
        next = request.path
    return next

def change(request, extra_context={}, next_override=None):
    avatars = Avatar.objects.filter(user=request.user).order_by('-primary')
    if avatars.count() > 0:
        avatar = avatars[0]
        kwargs = {'initial': {'choice': avatar.id}}
    else:
        avatar = None
        kwargs = {}
    primary_avatar_form = PrimaryAvatarForm(request.POST or None, user=request.user, **kwargs)
    if request.method == "POST":
        updated = False
        if 'avatar' in request.FILES:
            path = avatar_file_path(user=request.user, 
                filename=request.FILES['avatar'].name)
            avatar = Avatar(
                user = request.user,
                primary = True,
                avatar = path,
            )
            new_file = avatar.avatar.storage.save(path, request.FILES['avatar'])
            avatar.save()
            updated = True
            request.user.message_set.create(
                message=_("Successfully uploaded a new avatar."))
        if 'choice' in request.POST and primary_avatar_form.is_valid():
            avatar = Avatar.objects.get(id=
                primary_avatar_form.cleaned_data['choice'])
            avatar.primary = True
            avatar.save()
            updated = True
            request.user.message_set.create(
                message=_("Successfully updated your avatar."))
        if updated and notification:
            notification.send([request.user], "avatar_updated", {"user": request.user, "avatar": avatar})
            if friends:
                notification.send((x['friend'] for x in Friendship.objects.friends_for_user(request.user)), "avatar_friend_updated", {"user": request.user, "avatar": avatar})
        return HttpResponseRedirect(next_override or _get_next(request))
    return render_to_response(
        'avatar/change.html',
        extra_context,
        context_instance = RequestContext(
            request,
            { 'avatar': avatar, 
              'avatars': avatars,
              'primary_avatar_form': primary_avatar_form,
              'next': next_override or _get_next(request), }
        )
    )
change = login_required(change)

def delete(request, extra_context={}, next_override=None):
    avatars = Avatar.objects.filter(user=request.user).order_by('-primary')
    if avatars.count() > 0:
        avatar = avatars[0]
    else:
        avatar = None
    delete_avatar_form = DeleteAvatarForm(request.POST or None, user=request.user)
    if request.method == 'POST':
        if delete_avatar_form.is_valid():
            ids = delete_avatar_form.cleaned_data['choices']
            if unicode(avatar.id) in ids and avatars.count() > len(ids):
                for a in avatars:
                    if unicode(a.id) not in ids:
                        a.primary = True
                        a.save()
                        notification.send([request.user], "avatar_updated", {"user": request.user, "avatar": a})
                        if friends:
                            notification.send((x['friend'] for x in Friendship.objects.friends_for_user(request.user)), "avatar_friend_updated", {"user": request.user, "avatar": a})
                        break
            Avatar.objects.filter(id__in=ids).delete()
            request.user.message_set.create(
                message=_("Successfully deleted the requested avatars."))
            return HttpResponseRedirect(next_override or _get_next(request))
    return render_to_response(
        'avatar/confirm_delete.html',
        extra_context,
        context_instance = RequestContext(
            request,
            { 'avatar': avatar, 
              'avatars': avatars,
              'delete_avatar_form': delete_avatar_form,
              'next': next_override or _get_next(request), }
        )
    )
delete = login_required(delete)
