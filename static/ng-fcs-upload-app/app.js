/**
 * Created by swhite on 2/25/14.
 */

var app = angular.module('fcsUploadApp', ['ngRoute', 'ui.bootstrap', 'reflowService', 'angularFileUpload']);

app.config(function ($routeProvider) {
    $routeProvider
        .when('/',
        {
            controller: 'UploadController',
            templateUrl: '/static/ng-fcs-upload-app/partials/upload_samples.html'
        });
});