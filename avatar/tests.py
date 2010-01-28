import unittest
import os.path
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings

import avatar

try:
    from PIL import Image
except ImportError:
    import Image

from models import *

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
        
    # def testTooManyAvatars
    # def testReplaceAvatarWhenMaxIsOne
    # def testHashFileName
    # def testHashUserName
    # def testDeleteFile
    # def testChangePrimaryAvatar
    # def testAutomaticThumbnailCreation
