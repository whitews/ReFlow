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
        $scope.$on('projectUpdated', function () {
            $scope.projects = ModelService.getProjects();
        });
        $scope.user = ModelService.user;
        $scope.projects = ModelService.getProjects();
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

            $scope.current_project = get_project();

            $scope.$on('projectUpdated', function () {
                $scope.current_project = get_project();
            });

            $scope.errors = [];
            $scope.can_view_project = false;
            $scope.can_modify_project = false;
            $scope.can_add_data = false;
            $scope.can_manage_users = false;

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
        }
    ]
);

app.controller(
    'ProjectEditController',
    [
        '$scope',
        '$rootScope',
        'Project',
        function ($scope, $rootScope, Project) {

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

                response.$promise.then(function () {
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

            response.$promise.then(function () {
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
    'SubjectEditController',
    [
        '$scope',
        '$rootScope',
        '$controller',
        'Subject',
        'SubjectGroup',
        function ($scope, $rootScope, $controller, Subject, SubjectGroup) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.subject_groups = SubjectGroup.query(
                {
                    'project': $scope.current_project.id
                }
            );

            $scope.create_update = function (instance) {
                $scope.errors = [];
                var response;
                if (instance.id) {
                    response = Subject.update(
                        {id: instance.id },
                        $scope.instance
                    );
                } else {
                    instance.project = $scope.current_project.id;

                    response = Subject.save(
                        $scope.instance
                    );
                }

                response.$promise.then(function () {
                    // notify to update subject list
                    $rootScope.$broadcast('updateSubjects');

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
    'SiteController',
    [
        '$scope',
        '$controller',
        '$modal',
        'Site',
        function ($scope, $controller, $modal, Site) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            function get_list() {
                return Site.query(
                    {
                        'project': $scope.current_project.id
                    }
                );
            }
            $scope.sites = get_list();

            $scope.$on('updateSites', function () {
                $scope.sites = get_list();
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
    'SiteEditController',
    [
        '$scope',
        '$rootScope',
        '$controller',
        'Site',
        function ($scope, $rootScope, $controller, Site) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.create_update = function (instance) {
                $scope.errors = [];
                var response;
                if (instance.id) {
                    response = Site.update(
                        {id: instance.id },
                        $scope.instance
                    );
                } else {
                    instance.project = $scope.current_project.id;

                    response = Site.save(
                        $scope.instance
                    );
                }

                response.$promise.then(function () {
                    // notify to update subject list
                    $rootScope.$broadcast('updateSites');

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
                return Cytometer.query(
                    {
                        'project': $scope.current_project.id
                    }
                );
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
    'CytometerEditController',
    [
        '$scope',
        '$rootScope',
        '$controller',
        'Cytometer',
        'Site',
        function ($scope, $rootScope, $controller, Cytometer, Site) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.sites = Site.query(
                {
                    'project': $scope.current_project.id
                }
            );

            $scope.create_update = function (instance) {
                $scope.errors = [];
                var response;
                if (instance.id) {
                    response = Cytometer.update(
                        {id: instance.id },
                        $scope.instance
                    );
                } else {
                    response = Cytometer.save(
                        $scope.instance
                    );
                }

                response.$promise.then(function () {
                    // notify to update subject list
                    $rootScope.$broadcast('updateCytometers');

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
    'VisitTypeEditController',
    [
        '$scope',
        '$rootScope',
        '$controller',
        'VisitType',
        function ($scope, $rootScope, $controller, VisitType) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.create_update = function (instance) {
                $scope.errors = [];
                var response;
                if (instance.id) {
                    response = VisitType.update(
                        {id: instance.id },
                        $scope.instance
                    );
                } else {
                    instance.project = $scope.current_project.id;

                    response = VisitType.save(
                        $scope.instance
                    );
                }

                response.$promise.then(function () {
                    // notify to update subject list
                    $rootScope.$broadcast('updateVisitTypes');

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
]);

app.controller(
    'StimulationEditController',
    [
        '$scope',
        '$rootScope',
        '$controller',
        'Stimulation',
        function ($scope, $rootScope, $controller, Stimulation) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.create_update = function (instance) {
                $scope.errors = [];
                var response;
                if (instance.id) {
                    response = Stimulation.update(
                        {id: instance.id },
                        $scope.instance
                    );
                } else {
                    instance.project = $scope.current_project.id;

                    response = Stimulation.save(
                        $scope.instance
                    );
                }

                response.$promise.then(function () {
                    // notify to update subject list
                    $rootScope.$broadcast('updateStimulations');

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

            $scope.sites = Site.query(
                {
                    'project': $scope.current_project.id
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
                $scope.sites.forEach(function (s) {
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
                )
            };
            
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
    'SampleEditController',
    [
        '$scope',
        '$rootScope',
        '$controller',
        'Sample',
        'Subject',
        'VisitType',
        'Specimen',
        'Stimulation',
        'Pretreatment',
        'Storage',
        function ($scope, $rootScope, $controller, Sample, Subject, VisitType, Specimen, Stimulation, Pretreatment, Storage) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.subjects = Subject.query(
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

            $scope.specimens = Specimen.query();
            $scope.pretreatments = Pretreatment.query();
            $scope.storages = Storage.query();

            $scope.update = function (instance) {
                $scope.errors = [];
                var response;
                response = Sample.update(
                    {id: instance.id },
                    $scope.instance
                );

                response.$promise.then(function () {
                    // notify to update subject list
                    $rootScope.$broadcast('updateSamples');

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

            $scope.sites = Site.query(
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

                var sites = [];
                $scope.sites.forEach(function (s) {
                    if (s.query) {
                        sites.push(s.id);
                    }
                });

                $scope.samples = BeadSample.query(
                    {
                        'panel': panels,
                        'site': sites
                    }
                )
            };

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
    ['$scope', 'ModelService', function ($scope, ModelService) {
    }
]);