from django.conf.urls import include, url


urlpatterns = [
    url(r'^avatar/', include('avatar.urls')),
]
