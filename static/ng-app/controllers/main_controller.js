app.controller(
    'ModalController',
    [
        '$scope',
        '$modal',
        function ($scope, $modal) {
            // TODO: rename to init_modal?
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
    'MainController',
    [
        '$scope',
        '$controller',
        'ModelService',
        function ($scope, $controller, ModelService) {
            $controller('ModalController', {$scope: $scope});

            if (!$scope.projects) {
                $scope.projects = ModelService.getProjects();
            }

            $scope.$on('projects:updated', function () {
                $scope.projects = ModelService.getProjects();
            });

            $scope.user = ModelService.user;

            $scope.$on('current_project:updated', function () {
                $scope.current_project = ModelService.current_project;
            });
        }
    ]
);

app.controller(
    'ProjectDetailController',
    [
        '$scope',
        '$stateParams',
        'ModelService',
        function ($scope, $stateParams, ModelService) {
            // try to keep this controller as lean as possible because
            // many other controllers inherit this $scope to obtain the
            // "current project" and that results in this code executing
            if (!$scope.current_project && $stateParams.hasOwnProperty('projectId')) {
                ModelService.setCurrentProjectById($stateParams.projectId);
            } else if ($scope.current_project) {
                // also set current project if the current project doesn't
                if ($scope.current_project.id != parseInt($stateParams.projectId)) {
                    ModelService.setCurrentProjectById($stateParams.projectId);
                }
            }
        }
    ]
);

app.controller(
    'MarkerController',
    [
        '$scope',
        '$controller',
        'ModelService',
        function ($scope, $controller, ModelService) {
            // Inherit ProjectDetail scope to ensure current project is set via
            // $stateParams, important for browser refreshes & bookmarked URLs
            $controller('ProjectDetailController', {$scope: $scope});

            if ($scope.current_project) {
                $scope.markers = ModelService.getMarkers(
                    $scope.current_project.id
                );
            }

            $scope.$on('current_project:updated', function () {
                $scope.markers = ModelService.getMarkers(
                    $scope.current_project.id
                );
            });

            $scope.$on('markers:updated', function () {
                $scope.markers = ModelService.getMarkers(
                    $scope.current_project.id
                );
            });
        }
    ]
);

app.controller(
    'FluorochromeController',
    [
        '$scope',
        '$controller',
        'ModelService',
        function ($scope, $controller, ModelService) {
            // Inherit ProjectDetail scope to ensure current project is set via
            // $stateParams, important for browser refreshes & bookmarked URLs
            $controller('ProjectDetailController', {$scope: $scope});

            if ($scope.current_project) {
                $scope.fluorochromes = ModelService.getFluorochromes(
                    $scope.current_project.id
                );
            }

            $scope.$on('current_project:updated', function () {
                $scope.fluorochromes = ModelService.getFluorochromes(
                    $scope.current_project.id
                );
            });

            $scope.$on('fluorochromes:updated', function () {
                $scope.fluorochromes = ModelService.getFluorochromes(
                    $scope.current_project.id
                );
            });
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
        '$q',
        '$controller',
        'ModelService',
        function ($scope, $q, $controller, ModelService) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            function populate_cytometers() {
                var sites_can_add = ModelService.getProjectSitesWithAddPermission(
                    $scope.current_project.id
                ).$promise;

                var sites_can_modify = ModelService.getProjectSitesWithModifyPermission(
                    $scope.current_project.id
                ).$promise;

                var cytometers = ModelService.getCytometers(
                    {
                        'project': $scope.current_project.id
                    }
                ).$promise;

                $q.all([sites_can_add, sites_can_modify, cytometers]).then(function (objects) {
                    $scope.cytometers = objects[2];

                    // user has add privileges on at least one site
                    if (objects[0].length > 0) {
                        $scope.can_add_data = true;
                    }

                    $scope.cytometers.forEach(function (c) {
                        c.can_modify = false;

                        // check if cytometer's site is in modify list
                        for (var i=0; i<objects[1].length; i++) {
                            if (c.site == objects[1][i].id) {
                                c.can_modify = true;
                                break;
                            }
                        }
                    });
                });
            }

            if ($scope.current_project != undefined) {
                populate_cytometers();
            }
            $scope.$on('current_project:updated', function () {
                populate_cytometers();
            });

            $scope.$on('cytometers:updated', function () {
                populate_cytometers();
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
    'CellSubsetLabelController',
    [
        '$scope',
        '$controller',
        'ModelService',
        function ($scope, $controller, ModelService) {
            // Inherit ProjectDetail scope to ensure current project is set via
            // $stateParams, important for browser refreshes & bookmarked URLs
            $controller('ProjectDetailController', {$scope: $scope});

            if ($scope.current_project) {
                $scope.subset_labels = ModelService.getCellSubsetLabels(
                    $scope.current_project.id
                );
            }

            $scope.$on('current_project:updated', function () {
                $scope.subset_labels = ModelService.getCellSubsetLabels(
                    $scope.current_project.id
                );
            });

            $scope.$on('cell_subset_labels:updated', function () {
                $scope.subset_labels = ModelService.getCellSubsetLabels(
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
        function (
            $scope,
            $modal,
            $controller,
            ModelService
        ) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            // need to know which sites user can modify
            var sites_can_modify;
            function update_modify_sites () {
                sites_can_modify = ModelService.getProjectSitesWithModifyPermission(
                    $scope.current_project.id
                );
            }

            if ($scope.current_project) {
                init_filter();
                update_modify_sites();
            }

            $scope.$on('current_project:updated', function () {
                init_filter();
                update_modify_sites();
            });

            function init_filter () {
                $scope.panels = ModelService.getPanelTemplates(
                    {
                        'project': $scope.current_project.id
                    }
                );
                $scope.sites = ModelService.getProjectSitesWithAddPermission(
                    $scope.current_project.id
                );
                $scope.subjects = ModelService.getSubjects(
                    $scope.current_project.id
                );
                $scope.subject_groups = ModelService.getSubjectGroups(
                    $scope.current_project.id
                );
                $scope.visit_types = ModelService.getVisitTypes(
                    $scope.current_project.id
                );
                $scope.stimulations = ModelService.getStimulations(
                    $scope.current_project.id
                );
            }

            $scope.apply_filter = function () {
                $scope.errors = [];

                var panels = [];
                var panel_variants = [];
                $scope.panels.forEach(function (p) {
                    if (p.query) {
                        panels.push(p.id);
                    }

                    p.panel_variants.forEach(function (v) {
                        if (v.query) {
                            panel_variants.push(v.id);
                        }
                    });
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

                $scope.samples = ModelService.getSamples(
                    {
                        'project': $scope.current_project.id,
                        'panel': panels,
                        'panel_variant': panel_variants,
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
                            // check against sites_can_modify
                            for (var i=0; i<sites_can_modify.length; i++) {
                                if (s.site == sites_can_modify[i].id) {
                                    s.can_modify = true;
                                }
                            }
                        }
                    });
                });
            };

            $scope.$on('samples:updated', function () {
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

            $scope.show_metadata = function(instance) {
                // launch modal
                $modal.open({
                    templateUrl: MODAL_URLS.SAMPLE_METADATA,
                    controller: 'SampleMetadataController',
                    size: 'md',
                    resolve: {
                        instance: function() {
                            return instance;
                        }
                    }
                });
            };

            $scope.add_comp_from_sample = function(instance) {
                // launch modal
                $modal.open({
                    templateUrl: MODAL_URLS.COMPENSATION_FROM_SAMPLE,
                    controller: 'CompensationFromSampleController',
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
        'ModelService',
        function ($scope, $modalInstance, instance, ModelService) {
            $scope.instance = instance;
            $scope.ok = function () {
                $modalInstance.close();
            };

            $scope.site_panel = ModelService.getSitePanel(
                $scope.instance.site_panel
            );
        }
    ]
);

app.controller(
    'SampleMetadataController',
    [
        '$scope',
        '$modalInstance',
        'instance',
        'ModelService',
        function ($scope, $modalInstance, instance, ModelService) {
            $scope.instance = instance;
            $scope.ok = function () {
                $modalInstance.close();
            };

            $scope.metadata = ModelService.getSampleMetadata(
                {
                    'sample': $scope.instance.id
                }
            );
        }
    ]
);
