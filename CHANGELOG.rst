Changelog
=========

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
