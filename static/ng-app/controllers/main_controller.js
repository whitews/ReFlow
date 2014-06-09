app.controller(
    'MainController',
    ['$scope', function ($scope) {
        $scope.model = {};
    }
]);

app.controller(
    'ProjectQueryController',
    ['$scope', 'Project', function ($scope, Project) {
        $scope.model.projects = Project.query();

        $scope.model.projects.$promise.then(function (projects) {
            projects.forEach(function (p) {
                p.getUserPermissions().$promise.then(function (value) {
                    p.permissions = value.permissions;
                });
            });
        });
    }
]);