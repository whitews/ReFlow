app.controller(
    'MainController',
    ['$scope', function ($scope) {
        $scope.model = {};
    }
]);

app.controller(
    'ProjectQueryController',
    ['$scope', 'Project', 'Site', function ($scope, Project, Site) {
        $scope.model.projects = Project.query();

        $scope.model.projects.$promise.then(function (projects) {
            projects.forEach(function (p) {
                p.getUserPermissions().$promise.then(function (value) {
                    p.permissions = value.permissions;
                });

                // Add user's sites
                p.sites = [];
                var sites = Site.query({project: p.id});
                sites.$promise.then(function (sites) {
                    sites.forEach(function (s) {
                        p.sites.push(s);
                        s.getUserPermissions().$promise.then(function (value) {
                            s.permissions = value.permissions;
                        });
                    });
                });
            });
        });

        $scope.select_project = function (project) {
            $scope.model.current_project = project;
        }
    }
]);