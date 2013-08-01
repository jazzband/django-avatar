=============
django-avatar
=============

.. image:: https://secure.travis-ci.org/jezdez/django-avatar.png
    :target: http://travis-ci.org/jezdez/django-avatar

Django-avatar is a reusable application for handling user avatars.  It has the
ability to default to Gravatar if no avatar is found for a certain user.
Django-avatar automatically generates thumbnails and stores them to your default
file storage backend for retrieval later.

Using django-avatar
===================

Basics
------

To integrate ``django-avatar`` with your site, there are relatively few things
that are required.  A minimal integration can work like this:

1.  List this application in the ``INSTALLED_APPS`` portion of your settings
    file.  Your settings file will look something like::
   
        INSTALLED_APPS = (
            # ...
            'avatar',
        )

2.  Add the pagination urls to the end of your root urlconf.  Your urlconf
    will look something like::
    
        urlpatterns = patterns('',
            # ...
            (r'^avatar/', include('avatar.urls')),
        )

3.  Somewhere in your template navigation scheme, link to the change avatar
    page::
    
        <a href="{% url 'avatar_change' %}">Change your avatar</a>

4.  Wherever you want to display an avatar for a user, first load the avatar
    template tags::
    
        {% load avatar_tags %}
    
    Then, use the ``avatar`` tag to display an avatar of a default size::
    
        {% avatar user %}
    
    Or specify a size (in pixels) explicitly::
    
        {% avatar user 65 %}

5.  Optionally customize ``avatar/change.html`` and
    ``avatar/confirm_delete.html`` to conform to your site's look and feel.


Views
-----

There are only two views for this application: one for changing a user's avatar,
and another for deleting a user's avatar.

Changing an avatar
~~~~~~~~~~~~~~~~~~

The actual view function is located at ``avatar.views.change``, and this can
be referenced by the url name ``avatar_change``.  It takes two keyword
arguments: ``extra_context`` and ``next_override``.  If ``extra_context`` is
provided, that context will be placed into the template's context.  

If ``next_override`` is provided, the user will be redirected to the specified
URL after form submission.  Otherwise the user will be redirected to the URL
specified in the ``next`` parameter in ``request.POST``.  If ``request.POST``
has no ``next`` parameter, ``request.GET`` will be searched.  If ``request.GET``
has no ``next`` parameter, the ``HTTP_REFERER`` header will be inspected.  If
that header does not exist, the user will be redirected back to the current URL.

Deleting an avatar
~~~~~~~~~~~~~~~~~~

The actual view function is located at ``avatar.views.delete``, and this can be
referenced by the url name ``avatar_delete``.  It takes the same two keyword
arguments as ``avatar.views.change`` and follows the same redirection rules
as well.

Template Tags
-------------

To begin using these template tags, you must first load the tags into the
template rendering system:

    {% load avatar_tags %}

``{% avatar_url user [size in pixels] %}``
    Renders the URL of the avatar for the given user.  User can be either a
    ``django.contrib.auth.get_user_model()`` object instance or a username.

``{% avatar user [size in pixels] %}``
    Renders an HTML ``img`` tag for the given user for the specified size. User
    can be either a ``django.contrib.auth.get_user_model()`` object instance
    or a username.

``{% render_avatar avatar [size in pixels] %}``
    Given an actual ``avatar.models.Avatar`` object instance, renders an HTML
    ``img`` tag to represent that avatar at the requested size.


Global Settings
---------------

There are a number of settings available to easily customize the avatars that
appear on the site.  Listed below are those settings:

AVATAR_GRAVATAR_BASE_URL
    The base URL where to get avatars at gravatar.com. Defaults to ``http://www.gravatar.com/avatar/``.

AUTO_GENERATE_AVATAR_SIZES
    An iterable of integers representing the sizes of avatars to generate on
    upload.  This can save rendering time later on if you pre-generate the
    resized versions.  Defaults to ``(80,)``

AVATAR_RESIZE_METHOD
    The method to use when resizing images, based on the options available in
    PIL.  Defaults to ``Image.ANTIALIAS``.

AVATAR_STORAGE_DIR
    The directory under ``MEDIA_ROOT`` to store the images.  If using a
    non-filesystem storage device, this will simply be appended to the beginning
    of the file name.

AVATAR_GRAVATAR_BACKUP
    A boolean determining whether to default to the Gravatar service if no
    ``Avatar`` instance is found in the system for the given user.  Defaults to
    True.

AVATAR_DEFAULT_URL
    The default URL to default to if ``AVATAR_GRAVATAR_BACKUP`` is set to False
    and there is no ``Avatar`` instance found in the system for the given user.


Management Commands
-------------------

This application does include one management command: ``rebuild_avatars``.  It
takes no arguments and, when run, re-renders all of the thumbnails for all of
the avatars for the pixel sizes specified in the ``AUTO_GENERATE_AVATAR_SIZES``
setting.
