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
        $scope.$on('projectsUpdated', function () {
            $scope.projects = ModelService.getProjects();
        });

        if ($scope.projects === undefined) {
            ModelService.reloadProjects();
        }

        $scope.user = ModelService.user;
    }
]);

app.controller(
    'ProjectListController',
    [
        '$scope',
        '$controller',
        '$modal',
        'ModelService',
        function ($scope, $controller, $modal, ModelService) {
            // Inherits MainController $scope
            $controller('MainController', {$scope: $scope});

            $scope.init_form = function(instance) {
                var proposed_instance = angular.copy(instance);
                $scope.errors = [];

                // launch form modal
                var modalInstance = $modal.open({
                    templateUrl: MODAL_URLS.PROJECT,
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
    'ProjectDetailController',
    [
        '$scope',
        '$controller',
        '$stateParams',
        '$modal',
        'ModelService',
        function ($scope, $controller, $stateParams, $modal, ModelService) {
            // Inherits MainController $scope
            $controller('MainController', {$scope: $scope});

            function get_project() {
                return ModelService.getProjectById(
                    $stateParams.projectId
                );
            }

            if ($scope.projects === undefined) {
                ModelService.reloadProjects();
            } else {
                $scope.current_project = get_project();
            }

            $scope.$on('projectsUpdated', function () {
                $scope.current_project = get_project();
                $scope.$broadcast('currentProjectSet');
            });

            $scope.errors = [];
            $scope.can_view_project = false;
            $scope.can_modify_project = false;
            $scope.can_add_data = false;
            $scope.can_manage_users = false;

            $scope.$watch('current_project.permissions', function () {
                update_permissions();
            });

            function update_permissions() {
                if ($scope.current_project != null) {
                    if ($scope.current_project.permissions.indexOf('view_project_data') != -1 || $scope.user.superuser) {
                        $scope.can_view_project = true;
                    }
                    if ($scope.current_project.permissions.indexOf('add_project_data') != -1 || $scope.user.superuser) {
                        $scope.can_add_data = true;
                    }
                    if ($scope.current_project.permissions.indexOf('modify_project_data') != -1 || $scope.user.superuser) {
                        $scope.can_modify_project = true;
                    }
                    if ($scope.current_project.permissions.indexOf('submit_process_requests') != -1 || $scope.user.superuser) {
                        $scope.can_process_data = true;
                    }
                    if ($scope.current_project.permissions.indexOf('manage_project_users') != -1 || $scope.user.superuser) {
                        $scope.can_manage_users = true;
                    }
                }
            }

            $scope.init_form = function(instance, form_type) {
                var proposed_instance = angular.copy(instance);
                $scope.errors = [];

                // launch form modal
                var modalInstance = $modal.open({
                    templateUrl: MODAL_URLS[form_type],
                    controller: ModalFormCtrl,
                    resolve: {
                        instance: function() {
                            return proposed_instance;
                        }
                    }
                });
            };

            $scope.init_delete = function(instance, form_type) {
                $modal.open({
                    templateUrl: MODAL_URLS[form_type],
                    controller: ModalFormCtrl,
                    resolve: {
                        instance: function() {
                            return instance;
                        }
                    }
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

        if ($scope.current_project != undefined) {
            $scope.subject_groups = get_list();
        }
        $scope.$on('currentProjectSet', function () {
            $scope.subject_groups = get_list();
        });

        $scope.$on('updateSubjectGroups', function () {
            $scope.subject_groups = get_list();
        });

        $scope.init_form = function(instance) {
            var proposed_instance = angular.copy(instance);
            $scope.errors = [];

            // launch form modal
            var modalInstance = $modal.open({
                templateUrl: MODAL_URLS.SUBJECT_GROUP,
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
    'SubjectController',
    [
        '$scope',
        '$controller',
        '$modal',
        'Subject',
        function ($scope, $controller, $modal, Subject) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            function get_list() {
                return Subject.query(
                    {
                        'project': $scope.current_project.id
                    }
                );
            }
            $scope.subjects = get_list();

            $scope.$on('updateSubjects', function () {
                $scope.subjects = get_list();
            });

            $scope.init_form = function(instance) {
                var proposed_instance = angular.copy(instance);
                $scope.errors = [];

                // launch form modal
                var modalInstance = $modal.open({
                    templateUrl: MODAL_URLS.SUBJECT,
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
    'SiteController',
    [
        '$scope',
        '$controller',
        '$modal',
        'Site',
        function ($scope, $controller, $modal, Site) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.$on('updateSites', function () {
                $scope.current_project.update_sites();
            });

            $scope.init_form = function(instance) {
                var proposed_instance = angular.copy(instance);
                $scope.errors = [];

                // launch form modal
                $modal.open({
                    templateUrl: MODAL_URLS.SITE,
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
    'CytometerController',
    [
        '$scope',
        '$controller',
        '$modal',
        'Cytometer',
        function ($scope, $controller, $modal, Cytometer) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            function get_list() {
                var response = Cytometer.query(
                    {
                        'project': $scope.current_project.id
                    }
                );

                response.$promise.then(function (objects) {
                    objects.forEach(function (o) {
                        o.can_modify = false;
                        if ($scope.can_modify_project) {
                            o.can_modify = true;
                        } else {
                            var site = $scope.current_project.site_lookup[o.site];
                            if (site) {
                                if (site.can_modify) {
                                    o.can_modify = true;
                                }
                            }
                        }
                    });
                });

                return response;
            }
            $scope.cytometers = get_list();

            $scope.$on('updateCytometers', function () {
                $scope.cytometers = get_list();
            });

            $scope.init_form = function(instance) {
                var proposed_instance = angular.copy(instance);
                $scope.errors = [];

                // launch form modal
                var modalInstance = $modal.open({
                    templateUrl: MODAL_URLS.CYTOMETER,
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
    'VisitTypeController',
    [
        '$scope',
        '$controller',
        '$modal',
        'VisitType',
        function ($scope, $controller, $modal, VisitType) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            function get_list() {
                return VisitType.query(
                    {
                        'project': $scope.current_project.id
                    }
                );
            }
            $scope.visit_types = get_list();

            $scope.$on('updateVisitTypes', function () {
                $scope.visit_types = get_list();
            });

            $scope.init_form = function(instance) {
                var proposed_instance = angular.copy(instance);
                $scope.errors = [];

                // launch form modal
                $modal.open({
                    templateUrl: MODAL_URLS.VISIT_TYPE,
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
    'StimulationController',
    [
        '$scope',
        '$controller',
        '$modal',
        'Stimulation',
        function ($scope, $controller, $modal, Stimulation) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            function get_list() {
                return Stimulation.query(
                    {
                        'project': $scope.current_project.id
                    }
                );
            }
            $scope.stimulations = get_list();

            $scope.$on('updateStimulations', function () {
                $scope.stimulations = get_list();
            });

            $scope.init_form = function(instance) {
                var proposed_instance = angular.copy(instance);
                $scope.errors = [];

                // launch form modal
                $modal.open({
                    templateUrl: MODAL_URLS.STIMULATION,
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
    'SampleController',
    [
        '$scope',
        '$modal',
        '$controller',
        'ModelService',
        'Sample',
        'PanelTemplate',
        'Site',
        'Subject',
        'SubjectGroup',
        'VisitType',
        'Stimulation',
        function (
            $scope,
            $modal,
            $controller,
            ModelService,
            Sample,
            PanelTemplate,
            Site,
            Subject,
            SubjectGroup,
            VisitType,
            Stimulation
        ) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.panels = PanelTemplate.query(
                {
                    'project': $scope.current_project.id,
                    'staining': ['FS', 'US', 'FM', 'IS']
                }
            );

            $scope.subjects = Subject.query(
                {
                    'project': $scope.current_project.id
                }
            );

            $scope.subject_groups = SubjectGroup.query(
                {
                    'project': $scope.current_project.id
                }
            );

            $scope.visit_types = VisitType.query(
                {
                    'project': $scope.current_project.id
                }
            );

            $scope.stimulations = Stimulation.query(
                {
                    'project': $scope.current_project.id
                }
            );

            $scope.apply_filter = function () {
                $scope.errors = [];

                var panels = [];
                $scope.panels.forEach(function (p) {
                    if (p.query) {
                        panels.push(p.id);
                    }
                });

                var subject_groups = [];
                $scope.subject_groups.forEach(function (s) {
                    if (s.query) {
                        subject_groups.push(s.id);
                    }
                });

                var subjects = [];
                $scope.subjects.forEach(function (s) {
                    if (s.query) {
                        subjects.push(s.id);
                    }
                });

                var sites = [];
                $scope.current_project.sites.forEach(function (s) {
                    if (s.query) {
                        sites.push(s.id);
                    }
                });

                var visits = [];
                $scope.visit_types.forEach(function (v) {
                    if (v.query) {
                        visits.push(v.id);
                    }
                });

                var stimulations = [];
                $scope.stimulations.forEach(function (s) {
                    if (s.query) {
                        stimulations.push(s.id);
                    }
                });

                $scope.samples = Sample.query(
                    {
                        'panel': panels,
                        'subject_group': subject_groups,
                        'subject': subjects,
                        'site': sites,
                        'visit': visits,
                        'stimulation': stimulations
                    }
                );

                $scope.samples.$promise.then(function (samples) {
                    samples.forEach(function (s) {
                        s.can_modify = false;
                        if ($scope.can_modify_project) {
                            s.can_modify = true;
                        } else {
                            var site = $scope.current_project.site_lookup[s.site];
                            if (site) {
                                if (site.can_modify) {
                                    s.can_modify = true;
                                }
                            }
                        }
                    });
                })
            };

            $scope.$on('updateSamples', function () {
                $scope.apply_filter();
            });
            
            $scope.show_parameters = function(instance) {
                // launch modal
                $modal.open({
                    templateUrl: MODAL_URLS.SAMPLE_PARAMETERS,
                    controller: 'SampleParametersController',
                    size: 'lg',
                    resolve: {
                        instance: function() {
                            return instance;
                        }
                    }
                });
            };

            $scope.init_form = function(instance) {
                var proposed_instance = angular.copy(instance);
                $modal.open({
                    templateUrl: MODAL_URLS.SAMPLE,
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
    'SampleParametersController',
    [
        '$scope',
        '$modalInstance',
        'instance',
        'SitePanel',
        function ($scope, $modalInstance, instance, SitePanel) {
            $scope.instance = instance;
            $scope.ok = function () {
                $modalInstance.close();
            };

            $scope.site_panel = SitePanel.get(
                {id: $scope.instance.site_panel }
            );
        }
    ]
);

app.controller(
    'BeadSampleController',
    [
        '$scope',
        '$modal',
        '$controller',
        'ModelService',
        'BeadSample',
        'PanelTemplate',
        'Site',
        function (
            $scope,
            $modal,
            $controller,
            ModelService,
            BeadSample,
            PanelTemplate,
            Site
        ) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.panels = PanelTemplate.query(
                {
                    'project': $scope.current_project.id,
                    'staining': ['CB']
                }
            );

            $scope.apply_filter = function () {
                $scope.errors = [];

                var panels = [];
                $scope.panels.forEach(function (p) {
                    if (p.query) {
                        panels.push(p.id);
                    }
                });

                var sites = [];
                $scope.current_project.sites.forEach(function (s) {
                    if (s.query) {
                        sites.push(s.id);
                    }
                });

                $scope.samples = BeadSample.query(
                    {
                        'panel': panels,
                        'site': sites
                    }
                );

                $scope.samples.$promise.then(function (samples) {
                    samples.forEach(function (s) {
                        s.can_modify = false;
                        if ($scope.can_modify_project) {
                            s.can_modify = true;
                        } else {
                            var site = $scope.current_project.site_lookup[s.site];
                            if (site) {
                                if (site.can_modify) {
                                    s.can_modify = true;
                                }
                            }
                        }
                    });
                });
            };

            $scope.$on('updateBeadSamples', function () {
                $scope.apply_filter();
            });

            $scope.show_parameters = function(instance) {
                // launch modal
                $modal.open({
                    templateUrl: MODAL_URLS.SAMPLE_PARAMETERS,
                    controller: 'SampleParametersController',
                    size: 'lg',
                    resolve: {
                        instance: function() {
                            return instance;
                        }
                    }
                });
            };

            $scope.init_form = function(instance) {
                var proposed_instance = angular.copy(instance);
                $scope.errors = [];

                // launch form modal
                $modal.open({
                    templateUrl: MODAL_URLS.BEAD_SAMPLE,
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
    'CompensationController',
    [
        '$scope',
        '$controller',
        '$modal',
        'Compensation',
        function ($scope, $controller, $modal, Compensation) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            function get_list() {
                var response = Compensation.query(
                    {
                        'project': $scope.current_project.id
                    }
                );
                response.$promise.then(function (objects) {
                    objects.forEach(function (o) {
                        o.can_modify = false;
                        if ($scope.can_modify_project) {
                            o.can_modify = true;
                        } else {
                            var site = $scope.current_project.site_lookup[o.site];
                            if (site) {
                                if (site.can_modify) {
                                    o.can_modify = true;
                                }
                            }
                        }
                    });
                });

                return response;
            }
            $scope.compensations = get_list();

            $scope.$on('updateCompensations', function () {
                $scope.compensations = get_list();
            });

            $scope.init_form = function(instance) {
                var proposed_instance = angular.copy(instance);
                $scope.errors = [];

                // launch form modal
                $modal.open({
                    templateUrl: MODAL_URLS.COMPENSATION,
                    controller: ModalFormCtrl,
                    resolve: {
                        instance: function() {
                            return proposed_instance;
                        }
                    }
                });
            };

            $scope.show_matrix = function(instance) {
                $scope.errors = [];

                // launch form modal
                $modal.open({
                    templateUrl: MODAL_URLS.COMPENSATION_MATRIX,
                    controller: ModalFormCtrl,
                    size: 'lg',
                    resolve: {
                        instance: function() {
                            return instance;
                        }
                    }
                });
            };
        }
    ]
);