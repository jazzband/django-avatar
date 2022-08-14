Changelog
=========

* Unreleased
    * Allowed for rectangular avatars. The avatar tag template now requires the specification of a width and height independently.
    * Made ``True`` the default value of ``AVATAR_CLEANUP_DELETED``. (Set to ``False`` to obtain previous behavior).

* 6.0.1 (August 12, 2022)
    * Exclude tests folder from distribution.

* 6.0.0 (August 12, 2022)
    * Added Django 3.2, 4.0 and 4.1 support.
    * Removed Django 1.9, 1.10, 1.11, 2.0, 2.1, 2.2 and 3.0 support.
    * Added Python 3.9 and 3.10 support.
    * Removed Python 2.7, 3.4 and 3.5 support.
    * Made ``"PNG"`` the default value for ``AVATAR_THUMB_FORMAT`` (Set to ``"JPEG"`` to obtain previous behavior).
    * Made ``False`` the default value for ``AVATAR_EXPOSE_USERNAMES`` (Set to ``True`` to obtain previous behavior).
    * Don't leak usernames through image alt-tags when ``AVATAR_EXPOSE_USERNAMES`` is `False`.
    * New setting ``AVATAR_THUMB_MODES``. Default is ``['RGB', 'RGBA']``.
    * Use original image as thumbnail if thumbnail creation failed but image saving succeeds.
    * Add farsi translation.
    * Introduce black and flake8 linting

* 5.0.0 (January 4, 2019)
    * Added Django 2.1, 2.2, and 3.0 support.
    * Added Python 3.7 and 3.8 support.
    * Removed Python 1.9 and 1.10 support.
    * Fixed bug where avatars couldn't be deleted if file was already deleted.

* 4.1.0 (December 20, 2017)
    * Added Django 2.0 support.
    * Added ``avatar_deleted`` signal.
    * Ensure thumbnails are the correct orientation.

* 4.0.0 (May 27, 2017)
    * **Backwards incompatible:** Added ``AVATAR_PROVIDERS`` setting. Avatar providers are classes that return an avatar URL for a given user.
    * Added ``verbose_name`` to ``Avatar`` model fields.
    * Added the ability to override the ``alt`` attribute using the ``avatar`` template tag.
    * Added Italian translations.
    * Improved German translations.
    * Fixed bug where ``rebuild_avatars`` would fail on Django 1.10+.
    * Added Django 1.11 support.
    * Added Python 3.6 support.
    * Removed Django 1.7 and 1.8 support.
    * Removed Python 3.3 support.

* 3.1.0 (September 10, 2016)
    * Added the ability to override templates using ``AVATAR_ADD_TEMPLATE``, ``AVATAR_CHANGE_TEMPLATE``, and ``AVATAR_DELETE_TEMPLATE``.
    * Added the ability to pass additional HTML attributes using the ``{% avatar %}`` template tag.
    * Fixed unused verbosity setting in ``rebuild_avatars.py``.
    * Added Django 1.10 support
    * Removed Python 3.2 support

* 3.0.0 (February 26, 2016):
    * Added the ability to hide usernames/emails from avatar URLs.
    * Added the ability to use a Facebook Graph avatar as a backup.
    * Added a way to customize where avatars are stored.
    * Added a setting to disable the avatar cache.
    * Updated thumbnail creation to preserve RGBA.
    * Fixed issue where ``render_primary`` would not work if username/email was greater than 30 characters.
    * Fixed issue where cache was not invalidated after updating avatar
    * **Backwards Incompatible:** Renamed the ``avatar.util`` module to ``avatar.utils``.

* 2.2.1 (January 11, 2016)
    * Added AVATAR_GRAVATAR_FIELD setting to define the user field to get the gravatar email.
    * Improved Django 1.9/1.10 compatibility
    * Improved Brazilian translations

* 2.2.0 (December 2, 2015)
    * Added Python 3.5 support
    * Added Django 1.9 support
    * Removed Python 2.6 support
    * Removed Django 1.4, 1.5, and 1.6 support

* 2.1.1 (August 10, 2015)
    * Added Polish locale
    * Fixed RemovedInDjango19Warning warnings

* 2.1 (May 2, 2015)
    * Django 1.7 and 1.8 support
    * Add South and Django migrations
    * Changed Gravatar link to use HTTPS by default
    * Fixed a bug where the admin avatar list page would only show a user's primary avatar
    * Updated render_primary view to accept usernames with @ signs in them
    * Updated translations (added Dutch, Japanese, and Simple Chinese)
