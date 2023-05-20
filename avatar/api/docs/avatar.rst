
API Descriptions
================

Avatar List
^^^^^^^^^^^


send a request for listing user avatars as shown below.

``GET``  ``/api/avatar/``



    default response of avatar list : ::

         {
            "message": "You haven't uploaded an avatar yet. Please upload one now.",
            "default_avatar": {
                "src": "https://seccdn.libravatar.org/avatar/4a9328d595472d0728195a7c8191a50b",
                "width": "80",
                "height": "80",
                "alt": "User Avatar"
            }
        }


    if you have an avatar object : ::

        [
            {
                "id": "image_id",
                "avatar_url": "https://example.com/api/avatar/1/",
                "avatar": "https://example.com/media/avatars/1/first_avatar.png",
                "primary": true
            },
        ]



-----------------------------------------------

Create Avatar
^^^^^^^^^^^^^


send a request for creating user avatar as shown below .

``POST``  ``/api/avatar/``


    Request : ::

        {
            "avatar": "image file",
            "primary": true
        }

    ``Note`` : avatar field is required.

    Response : ::

        {
            "message": "Successfully uploaded a new avatar.",
            "data": {
                "id": "image_id",
                "avatar_url": "https://example.com/api/avatar/1/",
                "avatar": "https://example.com/media/avatars/1/example.png",
                "primary": true
                }
        }



-----------------------------------------------

Avatar Detail
^^^^^^^^^^^^^


send a request for retrieving user avatar.

``GET``  ``/api/avatar/image_id/``


    Response : ::

        {
            "id": "image_id",
            "avatar": "https://example.com/media/avatars/1/example.png",
            "primary": true
        }



-----------------------------------------------

Update Avatar
^^^^^^^^^^^^^


send a request for updating user avatar.

``PUT``  ``/api/avatar/image_id/``


    Request : ::

        {
            "avatar":"image file"
            "primary": true
        }

    ``Note`` : for update avatar image set ``API_AVATAR_CHANGE_IMAGE = True`` in your settings file and set ``primary = True``.

    Response : ::

        {
            "message": "Successfully updated your avatar.",
            "data": {
                "id": "image_id",
                "avatar": "https://example.com/media/avatars/1/custom_admin_en.png",
                "primary": true
            }
        }

-----------------------------------------------

Delete Avatar
^^^^^^^^^^^^^


send a request for deleting user avatar.

``DELETE``  ``/api/avatar/image_id/``


    Response : ::

        "Successfully deleted the requested avatars."




-----------------------------------------------

Render Primary Avatar
^^^^^^^^^^^^^^^^^^^^^

send a request for retrieving resized primary avatar .


default sizes ``80``:

``GET`` ``/api/avatar/render_primary/``

    Response : ::

        {
            "image_url": "https://example.com/media/avatars/1/resized/80/80/example.png"
        }

custom ``width`` and ``height`` :

``GET`` ``/api/avatar/render_primary/?width=width_size&height=height_size``

    Response : ::

        {
            "image_url": "http://127.0.0.1:8000/media/avatars/1/resized/width_size/height_size/python.png"
        }


If the entered parameter is one of ``width`` or ``height``, it will be considered for both .

``GET`` ``/api/avatar/render_primary/?width=size`` :

    Response : ::

        {
            "image_url": "http://127.0.0.1:8000/media/avatars/1/resized/size/size/python.png"
        }

``Note`` : Resize parameters not working for default avatar.

API Setting
===========

.. py:data:: API_AVATAR_CHANGE_IMAGE

    It Allows the user to Change the avatar image in ``PUT`` method. Default is ``False``.
