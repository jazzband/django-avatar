import django.dispatch


avatar_updated = django.dispatch.Signal(providing_args=["user", "avatar"])