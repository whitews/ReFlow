/**
 * Created by swhite on 2/25/14.
 */

var app = angular.module(
    'ProcessRequestApp',
    [
        'ngRoute',
        'ngSanitize',
        'ngCookies',
        'ui.bootstrap',
        'reflowService'
    ]
);

app.config(function ($routeProvider) {
    $routeProvider
        .when('/',
        {
            controller: 'ProcessRequestController',
            templateUrl: '/static/ng-process-request-app/partials/process_request.html'
        });
});
app.run(function ($http, $cookies) {
    $http.defaults.headers.common['X-CSRFToken'] = $cookies['csrftoken'];
});