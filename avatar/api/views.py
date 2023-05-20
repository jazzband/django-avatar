from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from avatar.api.serializers import AvatarSerializer
from avatar.api.utils import HTMLTagParser, assign_width_or_height, set_new_primary
from avatar.models import Avatar
from avatar.templatetags.avatar_tags import avatar
from avatar.utils import get_default_avatar_url, get_primary_avatar, invalidate_cache


class AvatarViewSets(viewsets.ModelViewSet):
    serializer_class = AvatarSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Avatar.objects.select_related("user").order_by(
        "-primary", "-date_uploaded"
    )

    @property
    def parse_html_to_json(self):
        default_avatar = avatar(self.request.user)
        html_parser = HTMLTagParser()
        html_parser.feed(default_avatar)
        return html_parser.output

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method." % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            return Response(data)

        return Response(
            {
                "message": "You haven't uploaded an avatar yet. Please upload one now.",
                "default_avatar": self.parse_html_to_json,
            }
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        message = _("Successfully uploaded a new avatar.")

        context_data = {"message": message, "data": serializer.data}
        return Response(context_data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.primary is True:
            # Find the next avatar, and set it as the new primary
            set_new_primary(self.get_queryset(), instance)
        self.perform_destroy(instance)
        message = _("Successfully deleted the requested avatars.")
        return Response(message, status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        avatar_image = serializer.validated_data.get("avatar")
        primary_avatar = serializer.validated_data.get("primary")
        if not primary_avatar and avatar_image:
            raise ValidationError("You cant update an avatar image that is not primary")

        if instance.primary is True:
            # Find the next avatar, and set it as the new primary
            set_new_primary(self.get_queryset(), instance)

        self.perform_update(serializer)
        invalidate_cache(request.user)
        message = _("Successfully updated your avatar.")
        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        context_data = {"message": message, "data": serializer.data}
        return Response(context_data)

    @action(
        ["GET"], detail=False, url_path="render_primary", name="Render Primary Avatar"
    )
    def render_primary(self, request, *args, **kwargs):
        """

        URL Example :

        1 - render_primary/
        2 - render_primary/?width=400  or  render_primary/?height=400
        3 - render_primary/?width=500&height=400
        """
        context_data = {}
        avatar_size = assign_width_or_height(request.query_params)

        width = avatar_size.get("width")
        height = avatar_size.get("height")

        primary_avatar = get_primary_avatar(request.user, width=width, height=height)

        if primary_avatar and primary_avatar.primary:
            url = primary_avatar.avatar_url(width, height)

        else:
            url = get_default_avatar_url()
            if bool(request.query_params):
                context_data.update(
                    {"message": "Resize parameters not working for default avatar"}
                )

        context_data.update({"image_url": request.build_absolute_uri(url)})
        return Response(context_data)
