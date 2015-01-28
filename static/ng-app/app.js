/**
 * Created by swhite on 6/9/14.
 */

var app = angular.module(
    'ReFlowApp',
    [
        'ngSanitize',
        'ngCookies',
        'ngResource',
        'ui.router',
        'ui.bootstrap',
        'ui.select2',
        'ncy-angular-breadcrumb',
        'angularFileUpload',
        'tableSort'
    ]
);

app.factory('LoginRedirectInterceptor', function($q, $window) {
    return {
        responseError: function(rejection) {
            if (rejection.status == 401) {
                $window.location.assign('/login');
            } else {
                return $q.reject(rejection);
            }
        }
    };
});

var MODAL_URLS = {
    'SUBJECT_GROUP':      'static/ng-app/partials/subject-group-form.html',
    'SUBJECT':            'static/ng-app/partials/subject-form.html',
    'PROJECT':            'static/ng-app/partials/project-form.html',
    'SITE':               'static/ng-app/partials/site-form.html',
    'CYTOMETER':          'static/ng-app/partials/cytometer-form.html',
    'VISIT_TYPE':         'static/ng-app/partials/visit-type-form.html',
    'CELL_SUBSET_LABEL':  'static/ng-app/partials/cell-subset-label-form.html',
    'STIMULATION':        'static/ng-app/partials/stimulation-form.html',
    'SAMPLE_PARAMETERS':  'static/ng-app/partials/sample-parameters-list.html',
    'SAMPLE_METADATA':    'static/ng-app/partials/sample-metadata-list.html',
    'SAMPLE':             'static/ng-app/partials/sample-form.html',
    'COMPENSATION':       'static/ng-app/partials/compensation-form.html',
    'COMPENSATION_MATRIX': 'static/ng-app/partials/compensation-matrix.html',
    'PROJECT_USER':       'static/ng-app/partials/project-user-form.html',
    'CHOOSE_USER':        'static/ng-app/partials/user-choose.html',
    'CHANGE_PASSWORD':    'static/ng-app/partials/user-change-password-form.html',

    // delete modals
    'SAMPLE_DELETE':      'static/ng-app/partials/sample-delete.html',
    'BEAD_SAMPLE_DELETE': 'static/ng-app/partials/bead-sample-delete.html',
    'COMPENSATION_DELETE': 'static/ng-app/partials/compensation-delete.html',
    'CYTOMETER_DELETE':   'static/ng-app/partials/cytometer-delete.html',
    'CELL_SUBSET_LABEL_DELETE': 'static/ng-app/partials/cell-subset-label-delete.html',
    'STIMULATION_DELETE': 'static/ng-app/partials/stimulation-delete.html',
    'VISIT_TYPE_DELETE':  'static/ng-app/partials/visit-type-delete.html',
    'SITE_DELETE':        'static/ng-app/partials/site-delete.html',
    'PANEL_DELETE':       'static/ng-app/partials/panel-template-delete.html',
    'SITE_PANEL_DELETE':  'static/ng-app/partials/site-panel-delete.html',
    'SUBJECT_DELETE':     'static/ng-app/partials/subject-delete.html',
    'SUBJECT_GROUP_DELETE': 'static/ng-app/partials/subject-group-delete.html',
    'PROJECT_DELETE':     'static/ng-app/partials/project-delete.html',
    'PROCESS_REQUEST_DELETE': 'static/ng-app/partials/process-request-delete.html',

    // admin modals
    'USER':               'static/ng-app/partials/user-form.html',
    'USER_DELETE':        'static/ng-app/partials/user-delete.html',
    'SPECIMEN':           'static/ng-app/partials/specimen-form.html',
    'SPECIMEN_DELETE':    'static/ng-app/partials/specimen-delete.html',
    'MARKER':             'static/ng-app/partials/marker-form.html',
    'MARKER_DELETE':      'static/ng-app/partials/marker-delete.html',
    'FLUOROCHROME':       'static/ng-app/partials/fluorochrome-form.html',
    'FLUOROCHROME_DELETE': 'static/ng-app/partials/fluorochrome-delete.html',
    'WORKER':             'static/ng-app/partials/worker-form.html',
    'WORKER_DELETE':      'static/ng-app/partials/worker-delete.html'
};

app.config(function ($stateProvider, $urlRouterProvider, $httpProvider) {
    $httpProvider.interceptors.push('LoginRedirectInterceptor');

    $urlRouterProvider.otherwise("/");

    $stateProvider.state({
        name: 'home',
        url: '/',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/home.html'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Projects'
        }
    }).state({
        name: 'user-profile',
        parent: 'home',
        url: 'user_profile/',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/user_profile.html'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'User Profile'
        }
    }).state({
        name: 'admin',
        parent: 'home',
        url: 'admin/',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/admin.html'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Admin'
        }
    }).state({
        name: 'specimen-list',
        parent: 'admin',
        url: 'specimens/',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/specimen-list.html',
                controller: 'SpecimenController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Specimens'
        }
    }).state({
        name: 'marker-list',
        parent: 'admin',
        url: 'markers/',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/marker-list.html',
                controller: 'MarkerController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Markers'
        }
    }).state({
        name: 'fluorochrome-list',
        parent: 'admin',
        url: 'fluorochromes/',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/fluorochrome-list.html',
                controller: 'FluorochromeController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Fluorochromes'
        }
    }).state({
        name: 'user-list',
        parent: 'admin',
        url: 'users/',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/user-list.html',
                controller: 'UserController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Users'
        }
    }).state({
        name: 'worker-list',
        parent: 'admin',
        url: 'workers/',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/worker-list.html',
                controller: 'WorkerController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Workers'
        }
    }).state({
        name: 'project-detail',
        parent: 'home',
        url: 'project/:projectId',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/project-detail.html',
                controller: 'ProjectDetailController'
            }
        },
        data: {
            ncyBreadcrumbLabel: '{{current_project.project_name}}'
        }
    }).state({
        name: 'process-request-list',
        parent: 'project-detail',
        url: '/process_request/',
        views: {
            '@': {
            templateUrl: '/static/ng-app/partials/process-request-list.html',
            controller: 'ProcessRequestController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Process Requests'
        }
    }).state({
        name: 'process-request-form',
        parent: 'project-detail',
        url: '/process_request/create',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/pr/process-request-form.html',
                controller: 'ProcessRequestFormController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Process Request'
        }
    }).state({
        name: 'process-request-detail',
        parent: 'process-request-list',
        url: ':requestId',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/process-request-detail.html',
                controller: 'ProcessRequestDetailController'
            }
        },
        data: {
            ncyBreadcrumbLabel: '{{process_request.description}}'
        }
    }).state({
        name: 'pr-visualization-detail',
        parent: 'process-request-detail',
        url: '/visualize',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/pr-visualization-detail.html',
                controller: 'PRVisualizationDetailController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Visualize'
        }
    }).state({
        name: 'project-user-list',
        parent: 'project-detail',
        url: '/users/',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/project-user-list.html',
                controller: 'ProjectUserController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Users'
        }
    }).state({
        name: 'subject-group-list',
        parent: 'project-detail',
        url: '/subject-groups/',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/subject-group-list.html',
                controller: 'SubjectGroupController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Subject Groups'
        }
    }).state({
        name: 'subject-list',
        parent: 'project-detail',
        url: '/subjects/',
        views: {
            '@': {
            templateUrl: '/static/ng-app/partials/subject-list.html',
            controller: 'SubjectController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Subjects'
        }
    }).state({
        name: 'site-list',
        parent: 'project-detail',
        url: '/sites/',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/site-list.html',
                controller: 'SiteController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Sites'
        }
    }).state({
        name: 'cytometer-list',
        parent: 'project-detail',
        url: '/cytometers/',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/cytometer-list.html',
                controller: 'CytometerController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Cytometers'
        }
    }).state({
        name: 'site-panel-list',
        parent: 'project-detail',
        url: '/sample-annotations/',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/site-panel-list.html',
                controller: 'SitePanelController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Sample Annotations'
        }
    }).state({
        name: 'visit-type-list',
        parent: 'project-detail',
        url: '/visit-types/',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/visit-type-list.html',
                controller: 'VisitTypeController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Visit Types'
        }
    }).state({
        name: 'stimulation-list',
        parent: 'project-detail',
        url: '/stimulations/',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/stimulation-list.html',
                controller: 'StimulationController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Stimulations'
        }
    }).state({
        name: 'cell-subset-label-list',
        parent: 'project-detail',
        url: '/cell-subset-labels/',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/cell-subset-label-list.html',
                controller: 'CellSubsetLabelController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Cell Subset Labels'
        }
    }).state({
        name: 'panel-template-list',
        parent: 'project-detail',
        url: '/panel-templates/',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/panel-template-list.html',
                controller: 'PanelTemplateController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Panel Templates'
        }
    }).state({
        name: 'panel-template-create',
        parent: 'panel-template-list',
        url: 'create',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/panel-template-create.html',
                controller: 'PanelTemplateCreateController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Create'
        }
    }).state({
        name: 'panel-template-edit',
        parent: 'panel-template-list',
        url: ':templateID/edit',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/panel-template-create.html',
                controller: 'PanelTemplateCreateController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Edit'
        }
    }).state({
        name: 'sample-list',
        parent: 'project-detail',
        url: '/samples/',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/sample-list.html',
                controller: 'SampleController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Samples'
        }
    }).state({
        name: 'sample-upload',
        parent: 'sample-list',
        url: 'upload',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/sample-upload.html',
                controller: 'MainSampleUploadController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Upload'
        }
    }).state({
        name: 'bead-sample-list',
        parent: 'project-detail',
        url: '/bead-samples/',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/bead-sample-list.html',
                controller: 'BeadSampleController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Bead Samples'
        }
    }).state({
        name: 'bead-sample-upload',
        parent: 'bead-sample-list',
        url: '/bead-samples/upload',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/bead-sample-upload.html',
                controller: 'MainSampleUploadController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Upload'
        }
    }).state({
        name: 'compensation-list',
        parent: 'project-detail',
        url: '/compensations/',
        views: {
            '@': {
                templateUrl: '/static/ng-app/partials/compensation-list.html',
                controller: 'CompensationController'
            }
        },
        data: {
            ncyBreadcrumbLabel: 'Compensation Matrices'
        }
    });
});

app.run(function ($http, $cookies) {
    $http.defaults.headers.common['X-CSRFToken'] = $cookies['csrftoken'];
});

app.filter('bytes', function() {
	return function(bytes, precision) {
		if (isNaN(parseFloat(bytes)) || !isFinite(bytes)) return '-';
		if (typeof precision === 'undefined') precision = 1;
		var units = ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'],
			number = Math.floor(Math.log(bytes) / Math.log(1024));
		return (bytes / Math.pow(1024, Math.floor(number))).toFixed(precision) +  ' ' + units[number];
	}
});

app.directive('closeModal', function (){
   return function(scope, elem, attrs) {
     scope.$watch('close_modal', function(val) {
        if(val) {
           elem.modal('hide');
        }
     });
   }
});