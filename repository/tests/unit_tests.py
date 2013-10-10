"""
This file contains unit tests for the repository Django app.
"""

from django.test import TestCase
from django.test.utils import override_settings
from django.conf.global_settings import FILE_UPLOAD_TEMP_DIR
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from guardian.shortcuts import assign_perm

from repository.models import *
from repository.forms import *
from repository.tests import constants


def testSetup():
    User.objects.create_superuser('supertester', password='supertester', email=None)
    User.objects.create_user('tester', password='tester', email=None)


@override_settings(MEDIA_ROOT=FILE_UPLOAD_TEMP_DIR)
class ModelsUnitTestCase(TestCase):

    fixtures = ['repository_models_tests.json']

    def setUp(self):
        testSetup()
        self.test_user = User.objects.get(username='tester')
        self.test_project = Project.objects.get(project_name='Project T')

    def test_user_has_no_projects(self):
        user_projects = Project.objects.get_projects_user_can_view(self.test_user)
        self.assertEqual(len(user_projects), 0)

    def test_user_has_projects(self):
        assign_perm('view_project_data', self.test_user, self.test_project)
        user_projects = Project.objects.get_projects_user_can_view(self.test_user)
        self.assertEqual(len(user_projects), 1)
        self.assertEqual(self.test_project.id, user_projects[0].id)

    def test_user_has_projects_based_on_site_access(self):
        projectX = Project.objects.get(project_name='Project X')
        projectX_site = Site.objects.get(site_name='Atlantis', project=projectX)
        assign_perm('view_site_data', self.test_user, projectX_site)
        user_projects = Project.objects.get_projects_user_can_view(self.test_user)
        self.assertEqual(len(user_projects), 1)

    def test_antibody_model(self):
        antibody = Antibody(antibody_abbreviation='IL-6')
        with self.assertRaises(ValidationError) as context:
            antibody.full_clean()

        self.assertEqual(
            context.exception.message_dict,
            {'antibody_name': [u'This field cannot be blank.']})


@override_settings(MEDIA_ROOT=FILE_UPLOAD_TEMP_DIR)
class ViewsUnitTestCase(TestCase):

    fixtures = ['repository_models_tests.json']

    def setUp(self):
        testSetup()

    def test_utility_views(self):
        """
        Utility views are login, logout, permission denied, not found, etc.
        """
        good_login = self.client.login(username='supertester', password='supertester')
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
        good_login = self.client.login(username='supertester', password='supertester')
        self.assertTrue(good_login)

        for view in constants.REGULAR_WEB_VIEWS:
            response = self.client.get(reverse(view))
            self.assertEqual(
                response.status_code,
                200,
                msg='%s != %s (View: %s)' % (response.status_code, 200, view))

    def test_admin_non_project_web_views(self):
        """
        Test admin views that do not require parameters
        """
        self.client.login(username='supertester', password='supertester')

        for view in constants.ADMIN_WEB_VIEWS:
            response = self.client.get(reverse(view), follow=True)
            self.assertEqual(
                response.status_code,
                200,
                msg='%s != %s (View: %s)' % (response.status_code, 200, view))

    def test_project_view(self):
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

    def test_antibody_views(self):
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
class FormsUnitTestCase(TestCase):

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
            'antibody_abbreviation': 'NA',
        }
        duplicate_form_data = {
            'antibody_name': 'NadaAntibody',
            'antibody_abbreviation': 'NA',
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

