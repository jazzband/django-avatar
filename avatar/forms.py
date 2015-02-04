import os

from django import forms
from django.forms import widgets
from django.utils import six
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat

from avatar.conf import settings
from avatar.models import Avatar


def avatar_img(avatar, size):
    if not avatar.thumbnail_exists(size):
        avatar.create_thumbnail(size)
    return mark_safe('<img src="%s" alt="%s" width="%s" height="%s" />' %
                     (avatar.avatar_url(size), six.text_type(avatar),
                      size, size))


class UploadAvatarForm(forms.Form):

    avatar = forms.ImageField(label=_("Avatar"))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(UploadAvatarForm, self).__init__(*args, **kwargs)

    def clean_avatar(self):
        data = self.cleaned_data['avatar']

        if settings.AVATAR_ALLOWED_MIMETYPES:
            try:
                import magic
            except ImportError:
                raise ImportError("python-magic library must be installed in "
                                  "order to use uploaded file content "
                                  "limitation")

            # Construct 256 bytes needed for mime validation
            magic_buffer = six.b('')
            for chunk in data.chunks():
                magic_buffer += chunk
                if len(magic_buffer) >= 256:
                    break

            # https://github.com/ahupp/python-magic#usage
            mime = magic.from_buffer(magic_buffer, mime=True)
            if six.PY3:
                mime = mime.decode('utf-8')
            if mime not in settings.AVATAR_ALLOWED_MIMETYPES:
                err = _(
                    "File content is invalid. Detected: %(mimetype)s "
                    "Allowed content types are: %(valid_mime_list)s"
                )

                conf = {
                    'valid_mime_list': ", ".join(settings.AVATAR_ALLOWED_MIMETYPES),
                    'mimetype': mime
                }

                raise forms.ValidationError(err % conf)

        if settings.AVATAR_ALLOWED_FILE_EXTS:
            root, ext = os.path.splitext(data.name.lower())
            if ext not in settings.AVATAR_ALLOWED_FILE_EXTS:
                valid_exts = ", ".join(settings.AVATAR_ALLOWED_FILE_EXTS)
                error = _("%(ext)s is an invalid file extension. "
                          "Authorized extensions are : %(valid_exts_list)s")
                raise forms.ValidationError(error %
                                            {'ext': ext,
                                             'valid_exts_list': valid_exts})

        if data.size > settings.AVATAR_MAX_SIZE:
            error = _("Your file is too big (%(size)s), "
                      "the maximum allowed size is %(max_valid_size)s")
            raise forms.ValidationError(error % {
                'size': filesizeformat(data.size),
                'max_valid_size': filesizeformat(settings.AVATAR_MAX_SIZE)
            })

        count = Avatar.objects.filter(user=self.user).count()
        if (settings.AVATAR_MAX_AVATARS_PER_USER > 1 and
                count >= settings.AVATAR_MAX_AVATARS_PER_USER):
            error = _("You already have %(nb_avatars)d avatars, "
                      "and the maximum allowed is %(nb_max_avatars)d.")
            raise forms.ValidationError(error % {
                'nb_avatars': count,
                'nb_max_avatars': settings.AVATAR_MAX_AVATARS_PER_USER,
            })

        return


class PrimaryAvatarForm(forms.Form):

    def __init__(self, *args, **kwargs):
        kwargs.pop('user')
        size = kwargs.pop('size', settings.AVATAR_DEFAULT_SIZE)
        avatars = kwargs.pop('avatars')
        super(PrimaryAvatarForm, self).__init__(*args, **kwargs)
        choices = [(avatar.id, avatar_img(avatar, size)) for avatar in avatars]
        self.fields['choice'] = forms.ChoiceField(label=_("Available avatars:"),
                                                  choices=choices,
                                                  widget=widgets.RadioSelect)


class DeleteAvatarForm(forms.Form):

    def __init__(self, *args, **kwargs):
        kwargs.pop('user')
        size = kwargs.pop('size', settings.AVATAR_DEFAULT_SIZE)
        avatars = kwargs.pop('avatars')
        super(DeleteAvatarForm, self).__init__(*args, **kwargs)
        choices = [(avatar.id, avatar_img(avatar, size)) for avatar in avatars]
        self.fields['choices'] = forms.MultipleChoiceField(label=_("Available avatars:"),
                                                           choices=choices,
                                                           widget=widgets.CheckboxSelectMultiple)
