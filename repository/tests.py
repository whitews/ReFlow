"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.utils import override_settings
from django.conf.global_settings import FILE_UPLOAD_TEMP_DIR
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from repository.models import *


@override_settings(MEDIA_ROOT=FILE_UPLOAD_TEMP_DIR)
class RepositoryModelsTest(TestCase):

    fixtures = ['repository_models_tests.json']

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

@override_settings(MEDIA_ROOT=FILE_UPLOAD_TEMP_DIR)
class RepositoryViewsTest(TestCase):

    fixtures = ['repository_models_tests.json']

    def setUp(self):
        User.objects.create_user('tester', password='tester')

    def test_login(self):
        """
        Test login view
        """
        good_login = self.client.login(username='tester', password='tester')
        self.assertTrue(good_login)

        bad_login = self.client.login(username="evil_user", password='letmein')
        self.assertFalse(bad_login)

    def test_web_views(self):
        self.client.login(username='tester', password='tester')

        # Test 'home' view
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        # Test 'view_antibodies' view
        response = self.client.get(reverse('view_antibodies'))
        self.assertEqual(response.status_code, 200)

        # Test 'add_antibodies' view, requires superuser so should return 403 response
        response = self.client.get(reverse('add_antibody'), follow=True)
        self.assertEqual(response.status_code, 403)
