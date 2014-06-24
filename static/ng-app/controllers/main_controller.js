var ModalFormCtrl = function ($scope, $modalInstance, instance) {
    $scope.instance = instance;
    $scope.ok = function () {
        $modalInstance.close();
    };
};

app.controller(
    'MainController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.$on('updateProjects', function () {
            ModelService.reloadProjects();
        });
    }
]);

app.controller(
    'ProjectListController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.projects = ModelService.getProjects();
    }
]);

app.controller(
    'ProjectDetailController',
    [
        '$scope',
        '$controller',
        '$stateParams',
        '$modal',
        'ModelService',
        function ($scope, $controller, $stateParams, $modal, ModelService) {
            function get_project() {
                return ModelService.getProjectById(
                    $stateParams.projectId
                );
            }

            $scope.current_project = get_project();

            $scope.$on('projectUpdated', function () {
                $scope.current_project = get_project();
            });

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

            $scope.init_form = function(instance) {
                var proposed_instance = angular.copy(instance);
                $scope.errors = [];

                // launch form modal
                var modalInstance = $modal.open({
                    templateUrl: 'static/ng-app/partials/project-form.html',
                    controller: ModalFormCtrl,
                    resolve: {
                        instance: function() {
                            return proposed_instance;
                        }
                    }
                });
            };
        }
    ]
);

app.controller(
    'ProjectEditController',
    [
        '$scope',
        '$rootScope',
        '$controller',
        'Project',
        function ($scope, $rootScope, $controller, Project) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.create_update = function (instance) {
                $scope.errors = [];
                var response;
                if (instance.id) {
                    response = Project.update(
                        {id: instance.id },
                        $scope.instance
                    );
                } else {
                    response = Project.save(
                        $scope.instance
                    );
                }

                response.$promise.then(function (o) {
                    // notify to update subject group list
                    $rootScope.$broadcast('updateProjects');

                    // close modal
                    $scope.ok();

                }, function (error) {
                    $scope.errors = error.data;
                });
            };
        }
    ]
);

app.controller(
    'SubjectGroupController',
    ['$scope', '$controller', '$stateParams', '$modal', 'SubjectGroup', function ($scope, $controller, $stateParams, $modal, SubjectGroup) {
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