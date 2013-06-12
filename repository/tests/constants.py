__author__ = 'swhite'

# Non-admin non-project specific web views (not REST API views)
REGULAR_WEB_VIEWS = (
    'home',
    'view_antibodies',
    'view_fluorochromes',
    'view_parameters',
    'view_specimens',
    'add_project',
    'view_sample_groups',
)

# Admin views not tied to a project and not REST API views
ADMIN_WEB_VIEWS = (
    'add_antibody',
    'add_fluorochrome',
    'add_parameter',
    'add_specimen',
    'add_sample_group',
)
