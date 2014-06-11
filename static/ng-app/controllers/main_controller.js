app.controller(
    'ProjectQueryController',
    ['$scope', 'ModelService', 'Project', 'Site', function ($scope, ModelService, Project, Site) {
        $scope.model = {};
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
            ModelService.updateCurrentProject(project);
        }
    }
]);

app.controller(
    'ProjectDetailController',
    ['$scope', 'ModelService', 'Project', 'Site', function ($scope, ModelService, Project, Site) {
        $scope.current_project = ModelService.getCurrentProject();
    }
]);