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
        'ModelService',
        function ($scope, ModelService) {
            $scope.current_project = ModelService.getCurrentProject();
            $scope.errors = [];
            $scope.can_view_project = false;
            $scope.can_modify_project = false;
            $scope.can_add_data = false;
            $scope.can_manage_users = false;

            if ($scope.current_project.permissions.indexOf('view_project_data')) {
                $scope.can_view_project = true;
            }
            if ($scope.current_project.permissions.indexOf('add_project_data')) {
                $scope.can_add_data = true;
            }
            if ($scope.current_project.permissions.indexOf('modify_project_data')) {
                $scope.can_modify_project = true;
            }
            if ($scope.current_project.permissions.indexOf('manage_project_users')) {
                $scope.can_manage_users = true;
            }
        }
    ]
);

app.controller(
    'ProjectEditController',
    [
        '$scope',
        '$location',
        'ModelService',
        'Project',
        function ($scope, $location, ModelService, Project) {
            $scope.current_project = ModelService.getCurrentProject();
            $scope.modified_project = angular.copy($scope.current_project);
            $scope.errors = [];

            $scope.updateProject = function () {
                $scope.errors = [];
                var project = Project.update(
                    {id:$scope.modified_project.id },
                    $scope.modified_project
                );

                project.$promise.then(function (o) {
                    // re-direct to project detail
                    ModelService.setCurrentProject($scope.modified_project);
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
    ['$scope', '$controller', 'SubjectGroup', function ($scope, $controller, SubjectGroup) {
        // Inherits ProjectDetailController $scope
        $controller('ProjectDetailController', {$scope: $scope});

        $scope.subject_groups = SubjectGroup.query(
            {
                'project': $scope.current_project.id
            }
        );
    }
]);

app.controller(
    'SubjectController',
    ['$scope', '$controller', 'Subject', function ($scope, $controller, Subject) {
        // Inherits ProjectDetailController $scope
        $controller('ProjectDetailController', {$scope: $scope});

        $scope.subjects = Subject.query(
            {
                'project': $scope.current_project.id
            }
        );
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