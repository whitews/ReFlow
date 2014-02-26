/**
 * Created by swhite on 2/25/14.
 */

var app = angular.module('fcsUploadApp', ['ngRoute']);

app.config(function ($routeProvider) {
    $routeProvider
        .when('/samples/upload/',
        {
            controller: 'UploadController',
            templateUrl: '/app/partials/upload_samples.html'
        })
});