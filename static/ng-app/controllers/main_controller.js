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
            ModelService.setCurrentProject(project);
        }
    }
]);

app.controller(
    'ProjectDetailController',
    [
        '$scope',
        '$location',
        'ModelService',
        'Project',
        function ($scope, $location, ModelService, Project) {
            $scope.current_project = ModelService.getCurrentProject();
            $scope.errors = [];
            $scope.can_view_project = false;
            $scope.can_modify_project = false;
            $scope.can_add_data = false;
            $scope.can_manage_users = false;

            if ($scope.current_project.permissions.indexOf('modify_project_data')) {
                $scope.can_modify_project = true;
            }
            if ($scope.current_project.permissions.indexOf('manage_project_users')) {
                $scope.can_manage_users = true;
            }

            $scope.updateProject = function () {
                $scope.errors = [];
                var project = Project.update(
                    {id:$scope.current_project.id },
                    $scope.current_project
                );

                project.$promise.then(function (o) {
                    // re-direct to project detail
                    $location.path('/project/');
                }, function(error) {

                    $scope.errors = error.data;
                });
            }

        }
    ]
);

app.controller(
    'SubjectGroupController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.getCurrentProject();
    }
]);

app.controller(
    'SubjectController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.getCurrentProject();
    }
]);

app.controller(
    'SiteController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.getCurrentProject();
    }
]);

app.controller(
    'CytometerController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.getCurrentProject();
    }
]);

app.controller(
    'VisitTypeController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.getCurrentProject();
    }
]);

app.controller(
    'StimulationController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.getCurrentProject();
    }
]);

app.controller(
    'PanelTemplateController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.getCurrentProject();
    }
]);

app.controller(
    'SampleController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.getCurrentProject();
    }
]);

app.controller(
    'BeadSampleController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.getCurrentProject();
    }
]);

app.controller(
    'CompensationController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.getCurrentProject();
    }
]);