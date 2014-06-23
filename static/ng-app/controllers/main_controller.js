var ModalFormCtrl = function ($scope, $modalInstance, instance) {
    $scope.instance = instance;
    $scope.ok = function () {
        $modalInstance.close();
    };
};

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
            };
        }
    ]
);

app.controller(
    'SubjectGroupController',
    ['$scope', '$controller', '$modal', 'SubjectGroup', function ($scope, $controller, $modal, SubjectGroup) {
        // Inherits ProjectDetailController $scope
        $controller('ProjectDetailController', {$scope: $scope});

        function get_list() {
            return SubjectGroup.query(
                {
                    'project': $scope.current_project.id
                }
            );
        }
        $scope.subject_groups = get_list();

        $scope.$on('updateSubjectGroups', function () {
            $scope.subject_groups = get_list();
        });

        $scope.init_form = function(instance) {
            var proposed_instance = angular.copy(instance);
            $scope.errors = [];

            // launch form modal
            var modalInstance = $modal.open({
                templateUrl: 'static/ng-app/partials/subject-group-form.html',
                controller: ModalFormCtrl,
                resolve: {
                    instance: function() {
                        return proposed_instance;
                    }
                }
            });
        };
    }
]);


app.controller(
    'SubjectGroupEditController',
    ['$scope', '$rootScope', '$controller', 'SubjectGroup', function ($scope, $rootScope, $controller, SubjectGroup) {
        // Inherits ProjectDetailController $scope
        $controller('ProjectDetailController', {$scope: $scope});

        $scope.create_update = function (instance) {
            $scope.errors = [];
            var response;
            if (instance.id) {
                response = SubjectGroup.update(
                    {id: instance.id },
                    $scope.instance
                );
            } else {
                instance.project = $scope.current_project.id;

                response = SubjectGroup.save(
                    $scope.instance
                );
            }

            response.$promise.then(function (o) {
                // notify to update subject group list
                $rootScope.$broadcast('updateSubjectGroups');

                // close modal
                $scope.ok();


            }, function (error) {
                $scope.errors = error.data;
            });
        };
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
    ['$scope', '$controller', 'Site', function ($scope, $controller, Site) {
        // Inherits ProjectDetailController $scope
        $controller('ProjectDetailController', {$scope: $scope});

        $scope.sites = Site.query(
            {
                'project': $scope.current_project.id
            }
        );
    }
]);

app.controller(
    'CytometerController',
    ['$scope', '$controller', 'Cytometer', function ($scope, $controller, Cytometer) {
        // Inherits ProjectDetailController $scope
        $controller('ProjectDetailController', {$scope: $scope});

        $scope.cytometers = Cytometer.query(
            {
                'project': $scope.current_project.id
            }
        );
    }
]);

app.controller(
    'VisitTypeController',
    ['$scope', '$controller', 'VisitType', function ($scope, $controller, VisitType) {
        // Inherits ProjectDetailController $scope
        $controller('ProjectDetailController', {$scope: $scope});

        $scope.visit_types = VisitType.query(
            {
                'project': $scope.current_project.id
            }
        );
    }
]);

app.controller(
    'StimulationController',
    ['$scope', '$controller', 'Stimulation', function ($scope, $controller, Stimulation) {
        // Inherits ProjectDetailController $scope
        $controller('ProjectDetailController', {$scope: $scope});

        $scope.stimulations = Stimulation.query(
            {
                'project': $scope.current_project.id
            }
        );
    }
]);

app.controller(
    'PanelTemplateController',
    ['$scope', '$controller', 'PanelTemplate', function ($scope, $controller, PanelTemplate) {
        // Inherits ProjectDetailController $scope
        $controller('ProjectDetailController', {$scope: $scope});

        $scope.panel_templates = PanelTemplate.query(
            {
                'project': $scope.current_project.id
            }
        );

        $scope.expand_params = [];
        $scope.panel_templates.$promise.then(function (o) {
            $scope.panel_templates.forEach(function () {
                $scope.expand_params.push(false);
            })
        });

        $scope.toggle_params = function (i) {
            $scope.expand_params[i] = $scope.expand_params[i] == true ? false:true;
        };

        $scope.expand_all_panels = function () {
            for (var i = 0; i < $scope.panel_templates.length; i++) {
                $scope.expand_params[i] = true;
            }
        };

        $scope.collapse_all_panels = function () {
            for (var i = 0; i < $scope.panel_templates.length; i++) {
                $scope.expand_params[i] = false;
            }
        };
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