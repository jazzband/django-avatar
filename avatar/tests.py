import os.path

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings

from avatar.settings import AVATAR_DEFAULT_URL, AVATAR_MAX_AVATARS_PER_USER
from avatar.util import get_primary_avatar, User
from avatar.models import Avatar

try:
    from PIL import Image
    dir(Image) # Placate PyFlakes
except ImportError:
    import Image
    

def upload_helper(o, filename):
    f = open(os.path.join(o.testdatapath, filename), "rb")
    response = o.client.post(reverse('avatar_add'), {
        'avatar': f,
    }, follow=True)
    f.close()
    return response

class AvatarUploadTests(TestCase):
    
    def setUp(self):
        self.testdatapath = os.path.join(os.path.dirname(__file__), "testdata")
        self.user = User.objects.create_user('test', 'lennon@thebeatles.com', 'testpassword')
        self.user.save()
        self.client.login(username='test', password='testpassword')
        Image.init()

    def testNonImageUpload(self):
        response = upload_helper(self, "nonimagefile")
        self.failUnlessEqual(response.status_code, 200)
        self.failIfEqual(response.context['upload_avatar_form'].errors, {})
        
    def testNormalImageUpload(self):
        response = upload_helper(self, "test.png")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.redirect_chain), 1)
        self.failUnlessEqual(response.context['upload_avatar_form'].errors, {})
        avatar = get_primary_avatar(self.user)
        self.failIfEqual(avatar, None)
        
    def testImageWithoutExtension(self):
        # use with AVATAR_ALLOWED_FILE_EXTS = ('.jpg', '.png')
        response = upload_helper(self, "imagefilewithoutext")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.redirect_chain), 0) # Redirect only if it worked        
        self.failIfEqual(response.context['upload_avatar_form'].errors, {})
        
    def testImageWithWrongExtension(self):
        # use with AVATAR_ALLOWED_FILE_EXTS = ('.jpg', '.png')
        response = upload_helper(self, "imagefilewithwrongext.ogg")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.redirect_chain), 0) # Redirect only if it worked        
        self.failIfEqual(response.context['upload_avatar_form'].errors, {})
        
    def testImageTooBig(self):
        # use with AVATAR_MAX_SIZE = 1024 * 1024
        response = upload_helper(self, "testbig.png")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.redirect_chain), 0) # Redirect only if it worked        
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
        
    def testThereCanBeOnlyOnePrimaryAvatar(self):
        for i in range(1, 10):
            self.testNormalImageUpload()
        count = Avatar.objects.filter(user=self.user, primary=True).count()
        self.failUnlessEqual(count, 1)
        
    def testDeleteAvatar(self):
        self.testNormalImageUpload()
        avatar = Avatar.objects.filter(user=self.user)
        self.failUnlessEqual(len(avatar), 1)
        response = self.client.post(reverse('avatar_delete'), {
            'choices': [avatar[0].id],
        }, follow=True)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.redirect_chain), 1)
        count = Avatar.objects.filter(user=self.user).count()
        self.failUnlessEqual(count, 0)
        
    def testDeletePrimaryAvatarAndNewPrimary(self):
        self.testThereCanBeOnlyOnePrimaryAvatar()
        primary = get_primary_avatar(self.user)
        oid = primary.id
        response = self.client.post(reverse('avatar_delete'), {
            'choices': [oid],
        })
        primaries = Avatar.objects.filter(user=self.user, primary=True)
        self.failUnlessEqual(len(primaries), 1)
        self.failIfEqual(oid, primaries[0].id)
        avatars = Avatar.objects.filter(user=self.user)
        self.failUnlessEqual(avatars[0].id, primaries[0].id)

    def testTooManyAvatars(self):
        for i in range(0, AVATAR_MAX_AVATARS_PER_USER):
            self.testNormalImageUpload()
        count_before = Avatar.objects.filter(user=self.user).count()       
        response = upload_helper(self, "test.png")
        count_after = Avatar.objects.filter(user=self.user).count()
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.redirect_chain), 0) # Redirect only if it worked
        self.failIfEqual(response.context['upload_avatar_form'].errors, {})
        self.failUnlessEqual(count_before, count_after)

    # def testAvatarOrder
    # def testReplaceAvatarWhenMaxIsOne
    # def testHashFileName
    # def testHashUserName
    # def testChangePrimaryAvatar
    # def testDeleteThumbnailAndRecreation    
    # def testAutomaticThumbnailCreation
