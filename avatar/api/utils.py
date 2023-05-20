from html.parser import HTMLParser

from avatar.conf import settings


class HTMLTagParser(HTMLParser):
    """
    URL parser for getting (url ,width ,height) from avatar templatetags
    """

    def __init__(self, output=None):
        HTMLParser.__init__(self)
        if output is None:
            self.output = {}
        else:
            self.output = output

    def handle_starttag(self, tag, attrs):
        self.output.update(dict(attrs))


def assign_width_or_height(query_params):
    """
    Getting width and height in url parameters and specifying them
    """
    avatar_default_size = settings.AVATAR_DEFAULT_SIZE

    width = query_params.get("width", avatar_default_size)
    height = query_params.get("height", avatar_default_size)

    if width == "":
        width = avatar_default_size
    if height == "":
        height = avatar_default_size

    if height == avatar_default_size and height != "":
        height = width
    elif width == avatar_default_size and width != "":
        width = height

    width = int(width)
    height = int(height)

    context = {"width": width, "height": height}
    return context


def set_new_primary(query_set, instance):
    queryset = query_set.exclude(id=instance.id).first()
    if queryset:
        queryset.primary = True
        queryset.save()
