/**
 * Created by swhite on 6/9/14.
 */

var app = angular.module(
    'ReFlowApp',
    [
        'ngSanitize',
        'ngCookies',
        'ui.router',
        'ui.bootstrap',
        'ui.select2',
        'ncy-angular-breadcrumb',
        'reflowService',
        'modelService',
        'angularFileUpload'
    ]
);

app.config(function ($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise("/");

    $stateProvider.state({
        name: 'home',
        url: '/',
        templateUrl: '/static/ng-app/partials/home.html',
        data: {
            ncyBreadcrumbLabel: 'Projects'
        }
    }).state({
        name: 'project-detail',
        url: '/project/',
        templateUrl: '/static/ng-app/partials/project-detail.html',
        controller: 'ProjectDetailController',
        data: {
            ncyBreadcrumbLabel: '{{current_project.project_name}}',
            ncyBreadcrumbParent: 'home'
        }
    }).state({
        name: 'project-edit',
        url: '/project/edit',
        templateUrl: '/static/ng-app/partials/project-edit.html',
        controller: 'ProjectDetailController',
        data: {
            ncyBreadcrumbLabel: 'Edit',
            ncyBreadcrumbParent: 'project-detail'
        }
    }).state({
        name: 'subject-group-list',
        url: '/subject-groups/',
        templateUrl: '/static/ng-app/partials/subject-group-list.html',
        controller: 'SubjectGroupController',
        data: {
            ncyBreadcrumbLabel: 'Subject Groups',
            ncyBreadcrumbParent: 'project-detail'
        }
    }).state({
        name: 'subject-group-add',
        url: '/subject-groups/add',
        templateUrl: '/static/ng-app/partials/subject-group-add.html',
        controller: 'SubjectGroupController',
        data: {
            ncyBreadcrumbLabel: 'Add',
            ncyBreadcrumbParent: 'subject-group-list'
        }
    }).state({
        name: 'subject-list',
        url: '/subjects/',
        templateUrl: '/static/ng-app/partials/subject-list.html',
        controller: 'SubjectController',
        data: {
            ncyBreadcrumbLabel: 'Subject Groups',
            ncyBreadcrumbParent: 'project-detail'
        }
    }).state({
        name: 'subject-add',
        url: '/subjects/add',
        templateUrl: '/static/ng-app/partials/subject-add.html',
        controller: 'SubjectController',
        data: {
            ncyBreadcrumbLabel: 'Add',
            ncyBreadcrumbParent: 'subject-list'
        }
    }).state({
        name: 'site-list',
        url: '/sites/',
        templateUrl: '/static/ng-app/partials/site-list.html',
        controller: 'SiteController',
        data: {
            ncyBreadcrumbLabel: 'Sites',
            ncyBreadcrumbParent: 'project-detail'
        }
    }).state({
        name: 'site-add',
        url: '/sites/add',
        templateUrl: '/static/ng-app/partials/site-add.html',
        controller: 'SiteController',
        data: {
            ncyBreadcrumbLabel: 'Add',
            ncyBreadcrumbParent: 'site-list'
        }
    }).state({
        name: 'cytometer-list',
        url: '/cytometers/',
        templateUrl: '/static/ng-app/partials/cytometer-list.html',
        controller: 'CytometerController',
        data: {
            ncyBreadcrumbLabel: 'Cytometers',
            ncyBreadcrumbParent: 'project-detail'
        }
    }).state({
        name: 'cytometer-add',
        url: '/cytometers/add',
        templateUrl: '/static/ng-app/partials/cytometer-add.html',
        controller: 'CytometerController',
        data: {
            ncyBreadcrumbLabel: 'Add',
            ncyBreadcrumbParent: 'cytometer-list'
        }
    }).state({
        name: 'visit-type-list',
        url: '/visit-types/',
        templateUrl: '/static/ng-app/partials/visit-type-list.html',
        controller: 'VisitTypeController',
        data: {
            ncyBreadcrumbLabel: 'Subject Groups',
            ncyBreadcrumbParent: 'project-detail'
        }
    }).state({
        name: 'visit-type-add',
        url: '/visit-types/add',
        templateUrl: '/static/ng-app/partials/visit-type-add.html',
        controller: 'VisitTypeController',
        data: {
            ncyBreadcrumbLabel: 'Add',
            ncyBreadcrumbParent: 'visit-type-list'
        }
    }).state({
        name: 'stimulation-list',
        url: '/stimulations/',
        templateUrl: '/static/ng-app/partials/stimulation-list.html',
        controller: 'StimulationController',
        data: {
            ncyBreadcrumbLabel: 'Subject Groups',
            ncyBreadcrumbParent: 'project-detail'
        }
    }).state({
        name: 'stimulation-add',
        url: '/stimulations/add',
        templateUrl: '/static/ng-app/partials/stimulation-add.html',
        controller: 'StimulationController',
        data: {
            ncyBreadcrumbLabel: 'Add',
            ncyBreadcrumbParent: 'stimulation-list'
        }
    }).state({
        name: 'panel-template-list',
        url: '/panel-templates/',
        templateUrl: '/static/ng-app/partials/panel-template-list.html',
        controller: 'PanelTemplateController',
        data: {
            ncyBreadcrumbLabel: 'Subject Groups',
            ncyBreadcrumbParent: 'project-detail'
        }
    }).state({
        name: 'panel-template-add',
        url: '/panel-templates/add',
        templateUrl: '/static/ng-app/partials/panel-template-add.html',
        controller: 'PanelTemplateController',
        data: {
            ncyBreadcrumbLabel: 'Add',
            ncyBreadcrumbParent: 'panel-template-list'
        }
    }).state({
        name: 'site-panel-list',
        url: '/site-panels/',
        templateUrl: '/static/ng-app/partials/site-panel-list.html',
        controller: 'SitePanelController',
        data: {
            ncyBreadcrumbLabel: 'Subject Groups',
            ncyBreadcrumbParent: 'project-detail'
        }
    }).state({
        name: 'sample-list',
        url: '/samples/',
        templateUrl: '/static/ng-app/partials/sample-list.html',
        controller: 'SampleController',
        data: {
            ncyBreadcrumbLabel: 'Subject Groups',
            ncyBreadcrumbParent: 'project-detail'
        }
    }).state({
        name: 'sample-add',
        url: '/samples/add',
        templateUrl: '/static/ng-app/partials/sample-add.html',
        controller: 'SampleController',
        data: {
            ncyBreadcrumbLabel: 'Add',
            ncyBreadcrumbParent: 'sample-list'
        }
    }).state({
        name: 'bead-sample-list',
        url: '/bead-samples/',
        templateUrl: '/static/ng-app/partials/bead-sample-list.html',
        controller: 'BeadSampleController',
        data: {
            ncyBreadcrumbLabel: 'Subject Groups',
            ncyBreadcrumbParent: 'project-detail'
        }
    }).state({
        name: 'bead-sample-add',
        url: '/bead-samples/add',
        templateUrl: '/static/ng-app/partials/bead-sample-add.html',
        controller: 'BeadSampleController',
        data: {
            ncyBreadcrumbLabel: 'Add',
            ncyBreadcrumbParent: 'bead-sample-list'
        }
    }).state({
        name: 'compensation-list',
        url: '/compensations/',
        templateUrl: '/static/ng-app/partials/compensation-list.html',
        controller: 'CompensationController',
        data: {
            ncyBreadcrumbLabel: 'Subject Groups',
            ncyBreadcrumbParent: 'project-detail'
        }
    }).state({
        name: 'compensation-add',
        url: '/compensations/add',
        templateUrl: '/static/ng-app/partials/compensation-add.html',
        controller: 'CompensationController',
        data: {
            ncyBreadcrumbLabel: 'Add',
            ncyBreadcrumbParent: 'compensation-list'
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
     scope.$watch('model.close_modal', function(val) {
        if(val) {
           elem.modal('hide');
        }
     });
   }
});