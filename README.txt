django-avatar
-------------

Django-avatar is a reusable application for handling user avatars.  It has the
ability to default to Gravatar if no avatar is found for a certain user.
Django-avatar automatically generates thumbnails and stores them to your default
file storage backend for retrieval later.


Addons to this fork:
----------------
we added a templatetag that returns the avatar model, therefore allowing us to display the avatar in any size using another image cropping/scaling app.