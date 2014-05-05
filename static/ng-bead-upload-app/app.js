var app = angular.module(
    'BeadUploadApp',
    [
        'ngRoute',
        'ngSanitize',
        'ngCookies',
        'ui.bootstrap',
        'ui.select2',
        'reflowService',
        'angularFileUpload'
    ]
);

app.config(function ($routeProvider) {
    $routeProvider
        .when('/',
        {
            controller: 'MainController',
            templateUrl: '/static/ng-bead-upload-app/partials/upload_beads.html'
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