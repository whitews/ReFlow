"""
This file contains integration tests for the repository Django app.
"""

from django.test import TestCase
from django.test.utils import override_settings
from django.conf.global_settings import FILE_UPLOAD_TEMP_DIR
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from guardian.shortcuts import assign_perm

from repository.models import *
from repository.forms import *


def testSetup():
    User.objects.create_superuser('supertester', password='supertester', email=None)
    User.objects.create_user('tester', password='tester', email=None)


@override_settings(MEDIA_ROOT=FILE_UPLOAD_TEMP_DIR)
class ViewsIntegrationTestCase(TestCase):

    fixtures = ['repository_models_tests.json']

    def setUp(self):
        testSetup()

    def test_project_view(self):
        """
        Test the creation and modification of Antibody model instances
        """

        # Test regular user without permission to view the project
        user = User.objects.get(username='tester')
        self.assertIsNotNone(user)
        login = self.client.login(username=user.username, password='tester')
        self.assertTrue(login)

        response = self.client.get(
            reverse(
                'view_project',
                kwargs={'project_id': '2'}),
            follow=True)
        self.assertEqual(response.status_code, 403)

        # Assign permission to view project and re-test
        assign_perm('view_project_data', user, Project.objects.get(pk='2'))
        response = self.client.get(
            reverse(
                'view_project',
                kwargs={'project_id': '2'}),
            follow=True)
        self.assertEqual(
            response.status_code,
            200)