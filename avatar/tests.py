import os.path

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.conf import settings

from django.contrib.auth.models import User

from avatar import AVATAR_DEFAULT_URL
from avatar.util import get_primary_avatar

try:
    from PIL import Image
    dir(Image) # Placate PyFlakes
except ImportError:
    import Image


class AvatarUploadTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.testdatapath = os.path.join(os.path.dirname(__file__), "testdata")
        self.user = User.objects.create_user('test', 'lennon@thebeatles.com', 'testpassword')
        self.user.save()
        self.client.login(username='test', password='testpassword')
        Image.init()

    def testNonImageUpload(self):
        f = open(os.path.join(self.testdatapath, "nonimagefile"), "rb")
        response = self.client.post(reverse('avatar_add'), {
            'avatar': f,
        })
        f.close()
        self.failUnlessEqual(response.status_code, 200)
        self.failIfEqual(response.context['upload_avatar_form'].errors, {})
        
    def testNormalImageUpload(self):
        f = open(os.path.join(self.testdatapath,"test.png"), "rb")
        response = self.client.post(reverse('avatar_add'), {
            'avatar': f,
        })
        f.close()
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['upload_avatar_form'].errors, {})
        avatar = get_primary_avatar(self.user)
        self.failIfEqual(avatar, None)
        
    def testImageWithoutExtension(self):
        f = open(os.path.join(self.testdatapath,"imagefilewithoutext"), "rb")
        response = self.client.post(reverse('avatar_add'), {
            'avatar': f,
        })
        f.close()
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['upload_avatar_form'].errors, {})
        
    def testImageWithWrongExtension(self):
        f = open(os.path.join(self.testdatapath,"imagefilewithwrongext.ogg"), "rb")
        response = self.client.post(reverse('avatar_add'), {
            'avatar': f,
        })
        f.close()
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['upload_avatar_form'].errors, {})
        
    def testImageTooBig(self):
        f = open(os.path.join(self.testdatapath,"testbig.png"), "rb")
        response = self.client.post(reverse('avatar_add'), {
            'avatar': f,
        })
        f.close()
        self.failUnlessEqual(response.status_code, 200)
        self.failIfEqual(response.context['upload_avatar_form'].errors, {})
    
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
        self.failUnlessEqual(a, None)

    # def testDeleteAvatar
    # def testDeletePrimaryAvatarAndNewPrimary
    # def testAvatarOrder
    # def testTooManyAvatars
    # def testReplaceAvatarWhenMaxIsOne
    # def testHashFileName
    # def testHashUserName
    # def testChangePrimaryAvatar
    # def testDeleteThumbnailAndRecreation    
    # def testAutomaticThumbnailCreation
