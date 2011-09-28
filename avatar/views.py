from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext as _
from django.views.generic.edit import BaseFormView, FormMixin
from django.views.generic.base import TemplateResponseMixin, View

from avatar.forms import PrimaryAvatarForm, DeleteAvatarForm, UploadAvatarForm
from avatar.models import Avatar
from avatar.settings import AVATAR_MAX_AVATARS_PER_USER, AVATAR_DEFAULT_SIZE
from avatar.signals import avatar_updated
from avatar.util import get_default_avatar_url


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

class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

class AvatarMixin(object):
    def get_target(self):
        return self.request.user

    def get_avatars(self, target):
        return _get_avatars(target)

    def create_avatar(self, target, avatar_file):
        avatar = Avatar(
                content_object=target,
                primary=True,
            )
        avatar.avatar.save(avatar_file.name, avatar_file)
        avatar.save()
        return avatar

    def get_success_url(self):
        return self.kwargs.get('next_override', None) or _get_next(self.request)

    def render_to_response(self, context):
        if self.request.is_ajax() or self.request.REQUEST.get('async', None) == 'true':
            return self.render_ajax_response(context)
        else:
            return TemplateResponseMixin.render_to_response(self, context)

    def render_ajax_response(self, context):
        return TemplateResponseMixin.render_to_response(self, context)

    def ajax_form_valid(self, new_avatar):
        return HttpResponse(new_avatar.avatar_url(AVATAR_DEFAULT_SIZE))

    def get_form_kwargs(self):
        kwargs = FormMixin.get_form_kwargs(self)
        kwargs['target'] = self.target
        kwargs['size'] = self.request.REQUEST.get('size', AVATAR_DEFAULT_SIZE)
        return kwargs

    def post(self, request, *args, **kwargs):
        self.target = self.get_target()
        self.avatar, self.avatars = self.get_avatars(self.target)
        return super(AvatarMixin, self).post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.target = self.get_target()
        self.avatar, self.avatars = self.get_avatars(self.target)
        return super(AvatarMixin, self).get(request, *args, **kwargs)

class AddAvatarView(LoginRequiredMixin, AvatarMixin, TemplateResponseMixin, BaseFormView):
    form_class = UploadAvatarForm
    template_name = "avatar/add.html"

    def form_valid(self, form):
        new_avatar = self.create_avatar(self.target, self.request.FILES['avatar'])
        if new_avatar:
            self.request.user.message_set.create(
                message=_("Successfully uploaded a new avatar."))
            avatar_updated.send(sender=Avatar, target=self.target,
                                avatar=new_avatar)
        if self.request.is_ajax() or self.request.REQUEST.get('async', None) == 'true':
            return self.ajax_form_valid(new_avatar)
        else:
            return FormMixin.form_valid(self, form)

    def get_context_data(self, **kwargs):
        kwargs['avatar'] = self.avatar
        kwargs['avatars'] = self.avatars
        kwargs['upload_avatar_form'] = kwargs['form']
        kwargs['next'] = self.get_success_url()
        return kwargs

class ChangeAvatarView(LoginRequiredMixin, AvatarMixin, TemplateResponseMixin, BaseFormView):
    form_class = PrimaryAvatarForm
    upload_form_class = UploadAvatarForm
    template_name = "avatar/change.html"

    def form_valid(self, form):
        new_avatar = Avatar.objects.get(id=form.cleaned_data['choice'])
        new_avatar.primary = True
        new_avatar.save()
        self.request.user.message_set.create(
            message=_("Avatar successfully updated."))
        avatar_updated.send(sender=Avatar, target=self.target, avatar=new_avatar)

        if self.request.is_ajax() or self.request.REQUEST.get('async', None) == 'true':
            return self.ajax_form_valid(new_avatar)
        else:
            return FormMixin.form_valid(self, form)

    def get_context_data(self, **kwargs):
        upload_form = self.upload_form_class(**self.get_form_kwargs())
        kwargs['avatar'] = self.avatar
        kwargs['avatars'] = self.avatars
        kwargs['target'] = self.target
        kwargs['primary_avatar_form'] = kwargs['form']
        kwargs['upload_avatar_form'] = upload_form
        kwargs['next'] = self.get_success_url()
        return kwargs

    def get_initial(self):
        initial = {}
        if self.avatar:
            initial['choice'] = self.avatar.id
            return initial
        else:
            return self.initial

class DeleteAvatarView(LoginRequiredMixin, AvatarMixin, TemplateResponseMixin, BaseFormView):
    form_class = DeleteAvatarForm
    template_name = "avatar/confirm_delete.html"

    def form_valid(self, form):
        ids = form.cleaned_data['choices']
        new_avatar = None
        if unicode(self.avatar.id) in ids and self.avatars.count() > len(ids):
            # Find the next best avatar, and set it as the new primary
            for a in self.avatars:
                if unicode(a.id) not in ids:
                    a.primary = True
                    a.save()
                    new_avatar = a
                    avatar_updated.send(sender=Avatar, target=self.target,
                                        avatar=a)
                    break
        Avatar.objects.filter(id__in=ids).delete()
        self.request.user.message_set.create(
            message=_("Successfully deleted the requested avatars."))
        if self.request.is_ajax() or self.request.REQUEST.get('async', None) == 'true':
            return self.ajax_form_valid(new_avatar)
        else:
            return FormMixin.form_valid(self, form)

    def get_context_data(self, **kwargs):
        kwargs['avatar'] = self.avatar
        kwargs['avatars'] = self.avatars
        kwargs['delete_avatar_form'] = kwargs['form']
        kwargs['next'] = self.get_success_url()
        return kwargs

class PrimaryAvatarView(AvatarMixin, View):
    def render_primary(self):
        size = self.kwargs.get('size', AVATAR_DEFAULT_SIZE)
        if self.avatar:
            # FIXME: later, add an option to render the resized avatar dynamically
            # instead of redirecting to an already created static file. This could
            # be useful in certain situations, particularly if there is a CDN and
            # we want to minimize the storage usage on our static server, letting
            # the CDN store those files instead
            return HttpResponseRedirect(self.avatar.avatar_url(size))
        else:
            url = get_default_avatar_url(self.target, size)
            return HttpResponseRedirect(url)

    def post(self, request, *args, **kwargs):
        super(self.__class__, self).post(request, *args, **kwargs)
        return self.render_primary()

    def get(self, request, *args, **kwargs):
        super(self.__class__, self).get(request, *args, **kwargs)
        return self.render_primary()
