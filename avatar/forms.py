import os

from django import forms
from django.forms import widgets
from django.template.defaultfilters import filesizeformat
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from avatar.conf import settings
from avatar.models import Avatar


def avatar_img(avatar, width, height):
    if not avatar.thumbnail_exists(width, height):
        avatar.create_thumbnail(width, height)
    return mark_safe(
        '<img src="%s" alt="%s" width="%s" height="%s" />'
        % (avatar.avatar_url(width, height), str(avatar), width, height)
    )


class UploadAvatarForm(forms.Form):
    avatar = forms.ImageField(label=_("avatar"))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean_avatar(self):
        data = self.cleaned_data["avatar"]

        if settings.AVATAR_ALLOWED_FILE_EXTS:
            root, ext = os.path.splitext(data.name.lower())
            if ext not in settings.AVATAR_ALLOWED_FILE_EXTS:
                valid_exts = ", ".join(settings.AVATAR_ALLOWED_FILE_EXTS)
                error = _(
                    "%(ext)s is an invalid file extension. "
                    "Authorized extensions are : %(valid_exts_list)s"
                )
                raise forms.ValidationError(
                    error % {"ext": ext, "valid_exts_list": valid_exts}
                )

        if data.size > settings.AVATAR_MAX_SIZE:
            error = _(
                "Your file is too big (%(size)s), "
                "the maximum allowed size is %(max_valid_size)s"
            )
            raise forms.ValidationError(
                error
                % {
                    "size": filesizeformat(data.size),
                    "max_valid_size": filesizeformat(settings.AVATAR_MAX_SIZE),
                }
            )

        count = Avatar.objects.filter(user=self.user).count()
        if 1 < settings.AVATAR_MAX_AVATARS_PER_USER <= count:
            error = _(
                "You already have %(nb_avatars)d avatars, "
                "and the maximum allowed is %(nb_max_avatars)d."
            )
            raise forms.ValidationError(
                error
                % {
                    "nb_avatars": count,
                    "nb_max_avatars": settings.AVATAR_MAX_AVATARS_PER_USER,
                }
            )
        return


class PrimaryAvatarForm(forms.Form):
    def __init__(self, *args, **kwargs):
        kwargs.pop("user")
        width = kwargs.pop("width", settings.AVATAR_DEFAULT_SIZE)
        height = kwargs.pop("height", settings.AVATAR_DEFAULT_SIZE)
        avatars = kwargs.pop("avatars")
        super().__init__(*args, **kwargs)
        self.fields["choice"] = forms.ChoiceField(
            choices=[(c.id, avatar_img(c, width, height)) for c in avatars],
            widget=widgets.RadioSelect,
        )


class DeleteAvatarForm(forms.Form):
    def __init__(self, *args, **kwargs):
        kwargs.pop("user")
        width = kwargs.pop("width", settings.AVATAR_DEFAULT_SIZE)
        height = kwargs.pop("height", settings.AVATAR_DEFAULT_SIZE)
        avatars = kwargs.pop("avatars")
        super().__init__(*args, **kwargs)
        self.fields["choices"] = forms.MultipleChoiceField(
            label=_("Choices"),
            choices=[(c.id, avatar_img(c, width, height)) for c in avatars],
            widget=widgets.CheckboxSelectMultiple,
        )
