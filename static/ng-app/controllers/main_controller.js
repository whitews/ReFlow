app.controller(
    'MainController',
    ['$scope', '$modal', 'ModelService',
        function ($scope, $modal, ModelService) {
            $scope.projects = ModelService.getProjects();

            $scope.$on('projects:updated', function () {
                $scope.projects = ModelService.getProjects();
            });

            $scope.user = ModelService.user;

            $scope.$on('current_project:updated', function () {
                $scope.current_project = ModelService.current_project;
            });

            $scope.init_form = function(instance, form_type) {
                var proposed_instance = angular.copy(instance);
                $scope.errors = [];

                // launch form modal
                var modalInstance = $modal.open({
                    templateUrl: MODAL_URLS[form_type],
                    controller: 'ModalFormCtrl',
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
        '$stateParams',
        '$modal',
        'ModelService',
        function ($scope, $stateParams, $modal, ModelService) {
            if (!$scope.current_project && $stateParams.hasOwnProperty('projectId')) {
                ModelService.setCurrentProjectById($stateParams.projectId);
            }
        }
    ]
);

app.controller(
    'SubjectGroupController',
    [
        '$scope',
        '$controller',
        'ModelService',
        function ($scope, $controller, ModelService) {
            // Inherit ProjectDetail scope to ensure current project is set via
            // $stateParams, important for browser refreshes & bookmarked URLs
            $controller('ProjectDetailController', {$scope: $scope});

            if ($scope.current_project) {
                $scope.subject_groups = ModelService.getSubjectGroups(
                    $scope.current_project.id
                );
            }

            $scope.$on('current_project:updated', function () {
                $scope.subject_groups = ModelService.getSubjectGroups(
                    $scope.current_project.id
                );
            });

            $scope.$on('subject_groups:updated', function () {
                $scope.subject_groups = ModelService.getSubjectGroups(
                    $scope.current_project.id
                );
            });
        }
    ]
);

app.controller(
    'SubjectController',
    [
        '$scope',
        '$controller',
        'ModelService',
        function ($scope, $controller, ModelService) {
            // Inherit ProjectDetail scope to ensure current project is set via
            // $stateParams, important for browser refreshes & bookmarked URLs
            $controller('ProjectDetailController', {$scope: $scope});

            if ($scope.current_project) {
                $scope.subjects = ModelService.getSubjects(
                    $scope.current_project.id
                );
            }

            $scope.$on('current_project:updated', function () {
                $scope.subjects = ModelService.getSubjects(
                    $scope.current_project.id
                );
            });

            $scope.$on('subjects:updated', function () {
                $scope.subjects = ModelService.getSubjects(
                    $scope.current_project.id
                );
            });
        }
    ]
);

app.controller(
    'SiteController',
    [
        '$scope',
        '$controller',
        'ModelService',
        function ($scope, $controller, ModelService) {
            // Inherit ProjectDetail scope to ensure current project is set via
            // $stateParams, important for browser refreshes & bookmarked URLs
            $controller('ProjectDetailController', {$scope: $scope});

            if ($scope.current_project) {
                $scope.sites = ModelService.getSites(
                    $scope.current_project.id
                );
            }

            $scope.$on('current_project:updated', function () {
                $scope.sites = ModelService.getSites(
                    $scope.current_project.id
                );
            });

            $scope.$on('sites:updated', function () {
                $scope.sites = ModelService.getSites(
                    $scope.current_project.id
                );
            });
        }
    ]
);

app.controller(
    'CytometerController',
    [
        '$scope',
        '$controller',
        'ModelService',
        function ($scope, $controller, ModelService) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            // TODO: still need to allow adding a cytometer if user has
            // add_site_data privileges for any site...will be tricky
            // look into ReFlow ModelManager method for Project???

            function get_list() {
                var response = ModelService.getCytometers(
                    {
                        'project': $scope.current_project.id
                    }
                );

                response.$promise.then(function (objects) {
                    objects.forEach(function (o) {
                        o.can_modify = false;

                        var site_perm_response = ModelService.getSitePermissions(o.site);
                        site_perm_response.$promise.then(function (s) {
                            if (s.hasOwnProperty('permissions')) {
                                if (s.permissions.indexOf('modify_site_data')) {
                                    o.can_modify = true;
                                }
                            }
                        });
                    });
                });

                return response;
            }

            if ($scope.current_project != undefined) {
                $scope.cytometers = get_list();
            }
            $scope.$on('current_project:updated', function () {
                $scope.cytometers = get_list();
            });

            $scope.$on('updateCytometers', function () {
                $scope.cytometers = get_list();
            });
        }
    ]
);

app.controller(
    'VisitTypeController',
    [
        '$scope',
        '$controller',
        'ModelService',
        function ($scope, $controller, ModelService) {
            // Inherit ProjectDetail scope to ensure current project is set via
            // $stateParams, important for browser refreshes & bookmarked URLs
            $controller('ProjectDetailController', {$scope: $scope});

            if ($scope.current_project) {
                $scope.visit_types = ModelService.getVisitTypes(
                    $scope.current_project.id
                );
            }

            $scope.$on('current_project:updated', function () {
                $scope.visit_types = ModelService.getVisitTypes(
                    $scope.current_project.id
                );
            });

            $scope.$on('visit_types:updated', function () {
                $scope.visit_types = ModelService.getVisitTypes(
                    $scope.current_project.id
                );
            });
        }
    ]
);

app.controller(
    'StimulationController',
    [
        '$scope',
        '$controller',
        'ModelService',
        function ($scope, $controller, ModelService) {
            // Inherit ProjectDetail scope to ensure current project is set via
            // $stateParams, important for browser refreshes & bookmarked URLs
            $controller('ProjectDetailController', {$scope: $scope});

            if ($scope.current_project) {
                $scope.stimulations = ModelService.getStimulations(
                    $scope.current_project.id
                );
            }

            $scope.$on('current_project:updated', function () {
                $scope.stimulations = ModelService.getStimulations(
                    $scope.current_project.id
                );
            });

            $scope.$on('stimulations:updated', function () {
                $scope.stimulations = ModelService.getStimulations(
                    $scope.current_project.id
                );
            });
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

            if ($scope.current_project != undefined) {
                init_filter();
            } else {
                $scope.$on('currentProjectSet', function () {
                    init_filter();
                });
            }

            function init_filter () {
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
            }

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
                        'project': $scope.current_project.id,
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
        function (
            $scope,
            $modal,
            $controller,
            ModelService,
            BeadSample,
            PanelTemplate
        ) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            if ($scope.current_project != undefined) {
                init_filter();
            } else {
                $scope.$on('currentProjectSet', function () {
                    init_filter();
                });
            }

            function init_filter () {
                $scope.panels = PanelTemplate.query(
                    {
                        'project': $scope.current_project.id,
                        'staining': ['CB']
                    }
                );
            }

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

            if ($scope.current_project != undefined) {
                $scope.compensations = get_list();
            } else {
                $scope.$on('currentProjectSet', function () {
                    $scope.compensations = get_list();
                });
            }

            $scope.$on('updateCompensations', function () {
                $scope.compensations = get_list();
            });

            $scope.show_matrix = function(instance) {
                $scope.errors = [];

                // launch form modal
                $modal.open({
                    templateUrl: MODAL_URLS.COMPENSATION_MATRIX,
                    controller: 'ModalFormCtrl',
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