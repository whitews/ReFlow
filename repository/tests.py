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

from guardian.shortcuts import assign_perm
from guardian.forms import UserObjectPermissionsForm

from repository.models import *
from repository.forms import *


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


def testSetup():
    User.objects.create_user('tester', password='tester', email=None)
    User.objects.create_superuser('supertester', password='supertester', email=None)


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
        testSetup()

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
        good_login = self.client.login(username='tester', password='tester')
        self.assertTrue(good_login)

        for view in __REGULAR_WEB_VIEWS__:
            response = self.client.get(reverse(view))
            self.assertEqual(
                response.status_code,
                200,
                msg='%s != %s (View: %s)' % (response.status_code, 200, view))

    def test_admin_non_project_web_views(self):
        """
        Test admin views that do not require parameters
        """
        self.client.login(username='tester', password='tester')

        for view in __ADMIN_WEB_VIEWS__:
            response = self.client.get(reverse(view), follow=True)
            self.assertEqual(
                response.status_code,
                403,
                msg='%s != %s (View: %s)' % (response.status_code, 403, view))

    def test_project_view(self):
        """
        Test the creation and modification of Antibody model instances
        """

        # Test superuser, has access to all projects
        superuser = User.objects.get(username='supertester')
        self.assertIsNotNone(superuser)
        login = self.client.login(username=superuser.username, password='supertester')
        self.assertTrue(login)

        response = self.client.get(
            reverse(
                'view_project',
                kwargs={'project_id': '2'}),
            follow=True)
        self.assertEqual(
            response.status_code,
            200)
        self.client.logout()

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
        self.assertEqual(
            response.status_code,
            403)

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

        # Using bad fields shouldn't redirect, should give a 200 to same page
        response = self.client.post(
            reverse('add_antibody'),
            data=data_bad_fields)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'antibody_name', "This field is required.")


@override_settings(MEDIA_ROOT=FILE_UPLOAD_TEMP_DIR)
class RepositoryFormsTest(TestCase):

    fixtures = ['repository_models_tests.json']

    def setUp(self):
        testSetup()

    def test_antibody_form(self):
        """
        Test Antibody ModelForm
        """

        bad_form_data = {
            'not_a_field': 43
        }
        good_form_data = {
            'antibody_name': 'NeuvoAntibody',
            'antibody_short_name': 'NA',
        }
        duplicate_form_data = {
            'antibody_name': 'NadaAntibody',
            'antibody_short_name': 'NA',
        }

        # Using bad data should give an invalid form
        bad_form = AntibodyForm(data=bad_form_data)
        self.assertEqual(bad_form.is_valid(), False)

        # And good data is good!
        good_form = AntibodyForm(data=good_form_data)
        self.assertEqual(good_form.is_valid(), True)
        good_form.save()

        # And duplicates ain't allowed
        duplicate_form = AntibodyForm(data=duplicate_form_data)
        self.assertEqual(duplicate_form.is_valid(), False)

