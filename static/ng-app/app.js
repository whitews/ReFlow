/**
 * Created by swhite on 6/9/14.
 */

var app = angular.module(
    'ReFlowApp',
    [
        'ui.router',
        'ngSanitize',
        'ngCookies',
        'ui.bootstrap',
        'ui.select2',
        'reflowService',
        'modelService',
        'angularFileUpload'
    ]
);

//app.config(function ($routeProvider) {
//    $routeProvider
//        .when('/',
//        {
//            templateUrl: '/static/ng-app/partials/home.html'
//        })
//        .when('/projects/:projectID',
//        {
//            templateUrl: '/static/ng-app/partials/project-detail.html'
//        });
//});

app.config(function ($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise("/");

    $stateProvider.state({
        name: 'home',
        url: '/',
        templateUrl: '/static/ng-app/partials/home.html'
    }).state({
        name: 'project-detail',
        url: '/projects/:projectID',
        templateUrl: '/static/ng-app/partials/project-detail.html'
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