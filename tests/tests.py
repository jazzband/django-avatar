import os.path

from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from avatar.admin import AvatarAdmin
from avatar.conf import settings
from avatar.utils import get_primary_avatar, get_user_model
from avatar.models import Avatar
from avatar.templatetags import avatar_tags
from PIL import Image


def upload_helper(o, filename):
    f = open(os.path.join(o.testdatapath, filename), "rb")
    response = o.client.post(reverse('avatar_add'), {
        'avatar': f,
    }, follow=True)
    f.close()
    return response


class AvatarTests(TestCase):

    def setUp(self):
        self.testdatapath = os.path.join(os.path.dirname(__file__), "data")
        self.user = get_user_model().objects.create_user('test', 'lennon@thebeatles.com', 'testpassword')
        self.user.save()
        self.client.login(username='test', password='testpassword')
        self.site = AdminSite()
        Image.init()

    def test_admin_get_avatar_returns_different_image_tags(self):
        self.test_normal_image_upload()
        self.test_normal_image_upload()
        primary = Avatar.objects.get(primary=True)
        old = Avatar.objects.get(primary=False)

        aa = AvatarAdmin(Avatar, self.site)
        primary_link = aa.get_avatar(primary)
        old_link = aa.get_avatar(old)

        self.assertNotEqual(primary_link, old_link)

    def test_non_image_upload(self):
        response = upload_helper(self, "nonimagefile")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.context['upload_avatar_form'].errors, {})

    def test_normal_image_upload(self):
        response = upload_helper(self, "test.png")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(response.context['upload_avatar_form'].errors, {})
        avatar = get_primary_avatar(self.user)
        self.assertIsNotNone(avatar)
        self.assertEqual(avatar.user, self.user)
        self.assertTrue(avatar.primary)

    def test_image_without_wrong_extension(self):
        # use with AVATAR_ALLOWED_FILE_EXTS = ('.jpg', '.png')
        response = upload_helper(self, "imagefilewithoutext")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 0)  # Redirect only if it worked
        self.assertNotEqual(response.context['upload_avatar_form'].errors, {})

    def test_image_with_wrong_extension(self):
        # use with AVATAR_ALLOWED_FILE_EXTS = ('.jpg', '.png')
        response = upload_helper(self, "imagefilewithwrongext.ogg")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 0)  # Redirect only if it worked
        self.assertNotEqual(response.context['upload_avatar_form'].errors, {})

    def test_image_too_big(self):
        # use with AVATAR_MAX_SIZE = 1024 * 1024
        response = upload_helper(self, "testbig.png")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 0)  # Redirect only if it worked
        self.assertNotEqual(response.context['upload_avatar_form'].errors, {})

    def test_default_url(self):
        response = self.client.get(reverse('avatar_render_primary', kwargs={
            'user': self.user.username,
            'size': 80,
        }))
        loc = response['Location']
        base_url = getattr(settings, 'STATIC_URL', None)
        if not base_url:
            base_url = settings.MEDIA_URL
        self.assertTrue(base_url in loc)
        self.assertTrue(loc.endswith(settings.AVATAR_DEFAULT_URL))

    def test_non_existing_user(self):
        a = get_primary_avatar("nonexistinguser")
        self.assertEqual(a, None)

    def test_there_can_be_only_one_primary_avatar(self):
        for i in range(1, 10):
            self.test_normal_image_upload()
        count = Avatar.objects.filter(user=self.user, primary=True).count()
        self.assertEqual(count, 1)

    def test_delete_avatar(self):
        self.test_normal_image_upload()
        avatar = Avatar.objects.filter(user=self.user)
        self.assertEqual(len(avatar), 1)
        response = self.client.post(reverse('avatar_delete'), {
            'choices': [avatar[0].id],
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 1)
        count = Avatar.objects.filter(user=self.user).count()
        self.assertEqual(count, 0)

    def test_delete_primary_avatar_and_new_primary(self):
        self.test_there_can_be_only_one_primary_avatar()
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

    def test_change_avatar_get(self):
        self.test_normal_image_upload()
        response = self.client.get(reverse('avatar_change'))

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['avatar'])

    def test_change_avatar_post_updates_primary_avatar(self):
        self.test_there_can_be_only_one_primary_avatar()
        old_primary = Avatar.objects.get(user=self.user, primary=True)
        choice = Avatar.objects.filter(user=self.user, primary=False)[0]
        response = self.client.post(reverse('avatar_change'), {
            'choice': choice.pk,
        })

        self.assertEqual(response.status_code, 302)
        new_primary = Avatar.objects.get(user=self.user, primary=True)
        self.assertEqual(new_primary.pk, choice.pk)
        # Avatar with old primary pk exists but it is not primary anymore
        self.assertTrue(Avatar.objects.filter(user=self.user, pk=old_primary.pk, primary=False).exists())

    def test_too_many_avatars(self):
        for i in range(0, settings.AVATAR_MAX_AVATARS_PER_USER):
            self.test_normal_image_upload()
        count_before = Avatar.objects.filter(user=self.user).count()
        response = upload_helper(self, "test.png")
        count_after = Avatar.objects.filter(user=self.user).count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 0)  # Redirect only if it worked
        self.assertNotEqual(response.context['upload_avatar_form'].errors, {})
        self.assertEqual(count_before, count_after)

    @override_settings(AVATAR_THUMB_FORMAT='png')
    def test_automatic_thumbnail_creation_RGBA(self):
        upload_helper(self, "django.png")
        avatar = get_primary_avatar(self.user)
        image = Image.open(avatar.avatar.storage.open(avatar.avatar_name(settings.AVATAR_DEFAULT_SIZE), 'rb'))
        self.assertEqual(image.mode, 'RGBA')

    def test_automatic_thumbnail_creation_CMYK(self):
        upload_helper(self, "django_pony_cmyk.jpg")
        avatar = get_primary_avatar(self.user)
        image = Image.open(avatar.avatar.storage.open(avatar.avatar_name(settings.AVATAR_DEFAULT_SIZE), 'rb'))
        self.assertEqual(image.mode, 'RGB')

    def test_has_avatar_False_if_no_avatar(self):
        self.assertFalse(avatar_tags.has_avatar(self.user))

    def test_has_avatar_False_if_not_user_model(self):
        self.assertFalse(avatar_tags.has_avatar("Look, I'm a string"))

    def test_has_avatar_True(self):
        upload_helper(self, "test.png")

        self.assertTrue(avatar_tags.has_avatar(self.user))

    def test_avatar_tag_works_with_username(self):
        upload_helper(self, "test.png")
        avatar = get_primary_avatar(self.user)

        result = avatar_tags.avatar(self.user.username)

        self.assertIn('<img src="{}"'.format(avatar.avatar_url(80)), result)
        self.assertIn('width="80" height="80" alt="test" />', result)

    def test_avatar_tag_works_with_user(self):
        upload_helper(self, "test.png")
        avatar = get_primary_avatar(self.user)

        result = avatar_tags.avatar(self.user)

        self.assertIn('<img src="{}"'.format(avatar.avatar_url(80)), result)
        self.assertIn('width="80" height="80" alt="test" />', result)

    def test_avatar_tag_works_with_custom_size(self):
        upload_helper(self, "test.png")
        avatar = get_primary_avatar(self.user)

        result = avatar_tags.avatar(self.user, 100)

        self.assertIn('<img src="{}"'.format(avatar.avatar_url(100)), result)
        self.assertIn('width="100" height="100" alt="test" />', result)

    def test_avatar_tag_works_with_kwargs(self):
        upload_helper(self, "test.png")
        avatar = get_primary_avatar(self.user)

        result = avatar_tags.avatar(self.user, title="Avatar")
        html = '<img src="{}" width="80" height="80" alt="test" title="Avatar" />'.format(avatar.avatar_url(80))
        self.assertInHTML(html, result)

    def test_default_add_template(self):
        response = self.client.get('/avatar/add/')
        self.assertContains(response, 'Upload New Image')
        self.assertNotContains(response, 'ALTERNATE ADD TEMPLATE')

    @override_settings(AVATAR_ADD_TEMPLATE='alt/add.html')
    def test_custom_add_template(self):
        response = self.client.get('/avatar/add/')
        self.assertNotContains(response, 'Upload New Image')
        self.assertContains(response, 'ALTERNATE ADD TEMPLATE')

    def test_default_change_template(self):
        response = self.client.get('/avatar/change/')
        self.assertContains(response, 'Upload New Image')
        self.assertNotContains(response, 'ALTERNATE CHANGE TEMPLATE')

    @override_settings(AVATAR_CHANGE_TEMPLATE='alt/change.html')
    def test_custom_change_template(self):
        response = self.client.get('/avatar/change/')
        self.assertNotContains(response, 'Upload New Image')
        self.assertContains(response, 'ALTERNATE CHANGE TEMPLATE')

    def test_default_delete_template(self):
        response = self.client.get('/avatar/delete/')
        self.assertContains(response, 'like to delete.')
        self.assertNotContains(response, 'ALTERNATE DELETE TEMPLATE')

    @override_settings(AVATAR_DELETE_TEMPLATE='alt/delete.html')
    def test_custom_delete_template(self):
        response = self.client.get('/avatar/delete/')
        self.assertNotContains(response, 'like to delete.')
        self.assertContains(response, 'ALTERNATE DELETE TEMPLATE')

    # def testAvatarOrder
    # def testReplaceAvatarWhenMaxIsOne
    # def testHashFileName
    # def testHashUserName
    # def testChangePrimaryAvatar
    # def testDeleteThumbnailAndRecreation
    # def testAutomaticThumbnailCreation
