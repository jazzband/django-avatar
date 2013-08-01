import os.path

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings

from avatar.settings import AVATAR_DEFAULT_URL, AVATAR_MAX_AVATARS_PER_USER
from avatar.util import get_primary_avatar, get_user_model
from avatar.models import Avatar
from PIL import Image


def upload_helper(o, filename):
    f = open(os.path.join(o.testdatapath, filename), "rb")
    response = o.client.post(reverse('avatar_add'), {
        'avatar': f,
    }, follow=True)
    f.close()
    return response


class AvatarUploadTests(TestCase):

    def setUp(self):
        self.testdatapath = os.path.join(os.path.dirname(__file__), "data")
        self.user = get_user_model().objects.create_user('test', 'lennon@thebeatles.com', 'testpassword')
        self.user.save()
        self.client.login(username='test', password='testpassword')
        Image.init()

    def testNonImageUpload(self):
        response = upload_helper(self, "nonimagefile")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.context['upload_avatar_form'].errors, {})

    def testNormalImageUpload(self):
        response = upload_helper(self, "test.png")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(response.context['upload_avatar_form'].errors, {})
        avatar = get_primary_avatar(self.user)
        self.assertNotEqual(avatar, None)

    def testImageWithoutExtension(self):
        # use with AVATAR_ALLOWED_FILE_EXTS = ('.jpg', '.png')
        response = upload_helper(self, "imagefilewithoutext")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 0)  # Redirect only if it worked
        self.assertNotEqual(response.context['upload_avatar_form'].errors, {})

    def testImageWithWrongExtension(self):
        # use with AVATAR_ALLOWED_FILE_EXTS = ('.jpg', '.png')
        response = upload_helper(self, "imagefilewithwrongext.ogg")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 0)  # Redirect only if it worked
        self.assertNotEqual(response.context['upload_avatar_form'].errors, {})

    def testImageTooBig(self):
        # use with AVATAR_MAX_SIZE = 1024 * 1024
        response = upload_helper(self, "testbig.png")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 0)  # Redirect only if it worked
        self.assertNotEqual(response.context['upload_avatar_form'].errors, {})

    def testDefaultUrl(self):
        response = self.client.get(reverse('avatar_render_primary', kwargs={
            'user': self.user.username,
            'size': 80,
        }))
        loc = response['Location']
        base_url = getattr(settings, 'STATIC_URL', None)
        if not base_url:
            base_url = settings.MEDIA_URL
        self.assertTrue(base_url in loc)
        self.assertTrue(loc.endswith(AVATAR_DEFAULT_URL))

    def testNonExistingUser(self):
        a = get_primary_avatar("nonexistinguser")
        self.assertEqual(a, None)

    def testThereCanBeOnlyOnePrimaryAvatar(self):
        for i in range(1, 10):
            self.testNormalImageUpload()
        count = Avatar.objects.filter(user=self.user, primary=True).count()
        self.assertEqual(count, 1)

    def testDeleteAvatar(self):
        self.testNormalImageUpload()
        avatar = Avatar.objects.filter(user=self.user)
        self.assertEqual(len(avatar), 1)
        response = self.client.post(reverse('avatar_delete'), {
            'choices': [avatar[0].id],
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 1)
        count = Avatar.objects.filter(user=self.user).count()
        self.assertEqual(count, 0)

    def testDeletePrimaryAvatarAndNewPrimary(self):
        self.testThereCanBeOnlyOnePrimaryAvatar()
        primary = get_primary_avatar(self.user)
        oid = primary.id
        self.client.post(reverse('avatar_delete'), {
            'choices': [oid],
        })
        primaries = Avatar.objects.filter(user=self.user, primary=True)
        self.assertEqual(len(primaries), 1)
        self.assertNotEqual(oid, primaries[0].id)
        avatars = Avatar.objects.filter(user=self.user)
        self.assertEqual(avatars[0].id, primaries[0].id)

    def testTooManyAvatars(self):
        for i in range(0, AVATAR_MAX_AVATARS_PER_USER):
            self.testNormalImageUpload()
        count_before = Avatar.objects.filter(user=self.user).count()
        response = upload_helper(self, "test.png")
        count_after = Avatar.objects.filter(user=self.user).count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 0)  # Redirect only if it worked
        self.assertNotEqual(response.context['upload_avatar_form'].errors, {})
        self.assertEqual(count_before, count_after)

    # def testAvatarOrder
    # def testReplaceAvatarWhenMaxIsOne
    # def testHashFileName
    # def testHashUserName
    # def testChangePrimaryAvatar
    # def testDeleteThumbnailAndRecreation
    # def testAutomaticThumbnailCreation
