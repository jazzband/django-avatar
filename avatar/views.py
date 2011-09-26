from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required

from avatar.forms import PrimaryAvatarForm, DeleteAvatarForm, UploadAvatarForm
from avatar.models import Avatar
from avatar.settings import AVATAR_MAX_AVATARS_PER_USER, AVATAR_DEFAULT_SIZE
from avatar.signals import avatar_updated
from avatar.util import (get_target_handler, get_primary_avatar,
                         get_default_avatar_url)
from avatar.templatetags.avatar_tags import avatar_url

def _get_next(request):
    """
    The part that's the least straightforward about views in this module is how 
    they determine their redirects after they have finished computation.

    In short, they will try and determine the next place to go in the following
    order:

    1. If there is a variable named ``next`` in the *POST* parameters, the view
    will redirect to that variable's value.
    2. If there is a variable named ``next`` in the *GET* parameters, the view
    will redirect to that variable's value.
    3. If Django can determine the previous page from the HTTP headers, the view
    will redirect to that previous page.
    """
    next = request.POST.get('next', request.GET.get('next',
        request.META.get('HTTP_REFERER', None)))
    if not next:
        next = request.path
    return next

def _get_avatars(target):
    # Default set. Needs to be sliced, but that's it. Keep the natural order.
    avatars = Avatar.objects.avatars_for_object(target)

    # Current avatar
    primary_avatar = avatars.order_by('-primary')[:1]
    if primary_avatar:
        avatar = primary_avatar[0]
    else:
        avatar = None

    if AVATAR_MAX_AVATARS_PER_USER == 1:
        avatars = primary_avatar
    else:
        # Slice the default set now that we used the queryset for the primary
        # avatar
        avatars = avatars[:AVATAR_MAX_AVATARS_PER_USER]
    return (avatar, avatars)

@login_required
def add(request, extra_context=None, next_override=None, target_type=None,
        target_id=None, upload_form=UploadAvatarForm, *args, **kwargs):
    if extra_context is None:
        extra_context = {}
    handler = get_target_handler()
    if target_type is None:
        target = request.user
    else:
        target = handler.get_target_from_type(target_type, target_id)
    avatar, avatars = _get_avatars(target)
    upload_form = handler.get_upload_form() or upload_form
    upload_avatar_form = upload_form(request.POST or None,
        request.FILES or None, target=target)
    if request.method == "POST" and 'avatar' in request.FILES:
        if upload_avatar_form.is_valid():
            new_avatar = handler.new_avatar(target, request.FILES['avatar'])
            if new_avatar:
                request.user.message_set.create(
                message=_("Successfully uploaded a new avatar."))
                avatar_updated.send(sender=Avatar, target=target,
                                    avatar=new_avatar)
                if request.is_ajax() or request.REQUEST.get('async', None) == 'true':
                    return HttpResponse(new_avatar.avatar_url(AVATAR_DEFAULT_SIZE))
                return HttpResponseRedirect(next_override or _get_next(request))
    return render_to_response(
            handler.add_template(request.is_ajax()),
            extra_context,
            context_instance=RequestContext(
                request,
                { 'avatar': avatar,
                  'avatars': avatars,
                  'upload_avatar_form': upload_avatar_form,
                  'next': next_override or _get_next(request), }
            )
        )

@login_required
def change(request, extra_context={}, next_override=None, target_type=None,
           target_id=None, upload_form=UploadAvatarForm,
           primary_form=PrimaryAvatarForm, *args, **kwargs):
    if extra_context is None:
        extra_context = {}
    handler = get_target_handler()
    if target_type is None:
        target = request.user
    else:
        target = handler.get_target_from_type(target_type, target_id)
    avatar, avatars = _get_avatars(target)
    upload_form = handler.get_upload_form() or upload_form
    primary_form = handler.get_primary_form() or primary_form
    if avatar:
        kwargs = {'initial': {'choice': avatar.id}}
    else:
        kwargs = {}
    upload_avatar_form = upload_form(target=target, **kwargs)
    kwargs['size'] = request.REQUEST.get('size', AVATAR_DEFAULT_SIZE)
    primary_avatar_form = primary_form(request.POST or None, avatars=avatars,
                                       **kwargs)
    if request.method == "POST":
        updated = False
        if 'choice' in request.POST and primary_avatar_form.is_valid():
            new_avatar = handler.get_avatar(target, primary_avatar_form.cleaned_data['choice'])
            new_avatar.primary = True
            new_avatar.save()
            updated = True
            request.user.message_set.create(
                message=_("Avatar successfully updated."))
        if updated:
            avatar_updated.send(sender=Avatar, target=target, avatar=new_avatar)
        if request.is_ajax():
            return HttpResponse(new_avatar.avatar_url(AVATAR_DEFAULT_SIZE))
        return HttpResponseRedirect(next_override or _get_next(request))
    return render_to_response(
        handler.change_template(request.is_ajax()),
        extra_context,
        context_instance=RequestContext(
            request,
            { 'avatar': avatar,
              'avatars': avatars,
              'target': target,
              'target_type': target_type,
              'id': target_id,
              'upload_avatar_form': upload_avatar_form,
              'primary_avatar_form': primary_avatar_form,
              'next': next_override or _get_next(request), }
        )
    )

@login_required
def delete(request, extra_context={}, next_override=None, target_type=None,
           target_id=None, *args, **kwargs):
    if extra_context is None:
        extra_context = {}
    handler = get_target_handler()
    if target_type is None:
        target = request.user
    else:
        target = handler.get_target_from_type(target_type, target_id)
    avatar, avatars = _get_avatars(target)
    delete_form = handler.get_delete_form() or DeleteAvatarForm
    delete_avatar_form = delete_form(request.POST or None, avatars=avatars)
    if request.method == 'POST':
        if delete_avatar_form.is_valid():
            ids = delete_avatar_form.cleaned_data['choices']
            if unicode(avatar.id) in ids and avatars.count() > len(ids):
                # Find the next best avatar, and set it as the new primary
                for a in avatars:
                    if unicode(a.id) not in ids:
                        a.primary = True
                        a.save()
                        avatar_updated.send(sender=Avatar, target=target,
                                            avatar=avatar)
                        break
            Avatar.objects.filter(id__in=ids).delete()
            request.user.message_set.create(
                message=_("Successfully deleted the requested avatars."))
            if request.is_ajax():
                return HttpResponse(avatar_url(target, AVATAR_DEFAULT_SIZE))
            return HttpResponseRedirect(next_override or _get_next(request))
    return render_to_response(
        handler.delete_template(request.is_ajax()),
        extra_context,
        context_instance=RequestContext(
            request,
            { 'avatar': avatar,
              'avatars': avatars,
              'delete_avatar_form': delete_avatar_form,
              'next': next_override or _get_next(request), }
        )
    )

def render_primary(request, extra_context={}, target_type=None, target_id=None,
                   size=AVATAR_DEFAULT_SIZE, *args, **kwargs):
    size = int(size)
    handler = get_target_handler()
    target = handler.get_target_from_type(target_type, target_id)
    avatar = get_primary_avatar(target, size=size)
    if avatar:
        # FIXME: later, add an option to render the resized avatar dynamically
        # instead of redirecting to an already created static file. This could
        # be useful in certain situations, particularly if there is a CDN and
        # we want to minimize the storage usage on our static server, letting
        # the CDN store those files instead
        return HttpResponseRedirect(avatar.avatar_url(size))
    else:
        url = get_default_avatar_url(target, size)
        return HttpResponseRedirect(url)
