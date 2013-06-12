__author__ = 'swhite'

"""
This package contains the test modules for the repository app of the ReFlow project,
organized by test type (unit, integration, etc.)

To run all the tests in the repository app, using the manage.py command:
"python manage.py test repository".

Notes:
- add new test constants in the constants module
"""


from unit_tests import *
from integration_tests import *
