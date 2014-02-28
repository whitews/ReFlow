/**
 * Created by swhite on 2/25/14.
 */
app.controller('UploadController', ['$scope', 'Project', 'Site', function ($scope, Project, Site) {
    $scope.projects = Project.query();

    $scope.updateMetadata = function () {
        if ($scope.current_project) {
            $scope.sites = Site.query({project: $scope.current_project.id});
        }
    };

}]);