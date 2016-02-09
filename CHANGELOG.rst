Changelog
=========

* 3.0 (Not released):
    * Added the ability to hide usernames/emails from avatar URLs.
    * Added the ability to use a Facebook Graph avatar as a backup.
    * Added a setting to disable the avatar cache.
    * Fixed issue where cache was not invalidated after updating avatar
    * Renamed the ``avatar.util`` module to ``avatar.utils``.

* 2.2.1 (January 11, 2016)
    * Added AVATAR_GRAVATAR_FIELD setting to define the user field to get the gravatar email.
    * Improved Django 1.9/1.10 compability
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
