/**
 * Created by swhite on 2/25/14.
 */

var app = angular.module('FCSUploadApp', ['ngRoute', 'ngSanitize', 'ngCookies', 'ui.bootstrap', 'reflowService', 'angularFileUpload']);

app.config(function ($routeProvider) {
    $routeProvider
        .when('/',
        {
            controller: 'MainController',
            templateUrl: '/static/ng-fcs-upload-app/partials/upload_samples.html'
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