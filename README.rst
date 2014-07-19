=============
django-avatar
=============

This is a fork of original https://github.com/jezdez/django-avatar . This one
is more updated as I merged more than 10 long-standing pull requests from the
original repository.

.. image:: https://secure.travis-ci.org/tbabej/django-avatar.png
    :target: http://travis-ci.org/tbabej/django-avatar

(travis builds refer to this fork)

Django-avatar is a reusable application for handling user avatars.  It has the
ability to default to Gravatar if no avatar is found for a certain user.
Django-avatar automatically generates thumbnails and stores them to your default
file storage backend for retrieval later.

For more information see the documentation at http://django-avatar.readthedocs.org/

Beware, the documentation online refers to the original project. For the documentation
of this fork, build the documentation from sources:

    sudo yum install python-sphinx -y
    cd docs
    make
