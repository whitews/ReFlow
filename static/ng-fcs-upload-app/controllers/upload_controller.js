/**
 * Created by swhite on 2/25/14.
 */
app.controller('UploadController', function ($scope, projectsService) {

    function init() {
        $scope.projects = projectsService.getProjects();
    }

});