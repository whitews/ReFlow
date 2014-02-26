/**
 * Created by swhite on 2/25/14.
 */
app.controller('UploadController', function ($scope, projectsService) {

    projectsService.getProjects().success(function (data) {
        $scope.projects = data;
    });

});