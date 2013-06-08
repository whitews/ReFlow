"""
This file contains tests for the repository app of the ReFlow project.
To run these tests:
"python manage.py test repository".

Notes:
- add new views by their named URL from repository.urls to the appropriate global set
"""

from django.test import TestCase
from django.test.utils import override_settings
from django.conf.global_settings import FILE_UPLOAD_TEMP_DIR
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from repository.models import *

# Non-admin non-project specific web views (not REST API views)
__REGULAR_WEB_VIEWS__ = (
    'home',
    'view_antibodies',
    'view_fluorochromes',
    'view_parameters',
    'view_specimens',
    'add_project',
    'view_sample_groups',
)

# Admin views not tied to a project and not REST API views
__ADMIN_WEB_VIEWS__ = (
    'add_antibody',
    'add_fluorochrome',
    'add_parameter',
    'add_specimen',
    'add_sample_group',
)


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
        User.objects.create_user('tester', password='tester', email=None)
        User.objects.create_superuser('supertester', password='supertester', email=None)

    def test_utility_views(self):
        """
        Test login view
        """
        good_login = self.client.login(username='tester', password='tester')
        self.assertTrue(good_login)

        bad_login = self.client.login(username="evil_user", password='letmein')
        self.assertFalse(bad_login)

        response = self.client.get(reverse('permission_denied'))
        self.assertEqual(
            response.status_code,
            403,
            msg='%s != %s (View: %s)' % (response.status_code, 403, 'permission_denied'))

    def test_non_admin_non_project_web_views(self):
        """
        Test non-project views that do not require parameters
        """
        self.client.login(username='tester', password='tester')
        expected_response_code = 200

        for view in __REGULAR_WEB_VIEWS__:
            response = self.client.get(reverse(view))
            self.assertEqual(
                response.status_code,
                expected_response_code,
                msg='%s != %s (View: %s)' % (response.status_code, expected_response_code, view))

    def test_admin_non_project_web_views(self):
        """
        Test admin views that do not require parameters
        """
        self.client.login(username='tester', password='tester')
        expected_response_code = 403

        for view in __ADMIN_WEB_VIEWS__:
            response = self.client.get(reverse(view), follow=True)
            self.assertEqual(
                response.status_code,
                expected_response_code,
                msg='%s != %s (View: %s)' % (response.status_code, expected_response_code, view))

    def test_antibody_add_edit(self):
        """
        Test the creation and modification of Antibody model instances
        """
        user = User.objects.get(username='supertester')
        self.assertIsNotNone(user)
        login = self.client.login(username=user.username, password='supertester')
        self.assertTrue(login)

        data_bad_fields = {
            'not_a_field': 43
        }
        import os
        from reflow import settings
        print os.environ['PWD']
        print settings.TEMPLATE_DIRS
        # Using bad fields shouldn't redirect, should give a 200 to same page
        response = self.client.post(
            reverse('add_antibody'),
            data=data_bad_fields)
        self.assertEqual(response.status_code, 200)
