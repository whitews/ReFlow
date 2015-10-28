app.controller(
    'ProjectEditController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.current_project = ModelService.current_project;

            $scope.create_update = function (instance) {
                if (!instance) {
                    $scope.errors = [
                        "Please fill out the required fields"
                    ];
                    return;
                }

                $scope.errors = [];
                var response = ModelService.createUpdateProject(instance);

                response.$promise.then(function (object) {
                    // notify to update project list
                    ModelService.projectsUpdated();

                    // also check if this is the current project
                    if ($scope.current_project) {
                        if (object.id == $scope.current_project.id) {
                            ModelService.setCurrentProjectById(object.id);
                        }
                    }

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
    'MarkerEditController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.current_project;

        $scope.create_update = function (instance) {
            $scope.errors = [];
            if (!instance.id) {
                instance.project = $scope.current_project.id;
            }
            var response = ModelService.createUpdateMarker(instance);

            response.$promise.then(function () {
                // notify to update list
                ModelService.markersUpdated();

                // close modal
                $scope.ok();

            }, function (error) {
                $scope.errors = error.data;
            });
        };
        }
]);

app.controller(
    'FluorochromeEditController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.current_project;

        $scope.create_update = function (instance) {
            $scope.errors = [];
            if (!instance.id) {
                instance.project = $scope.current_project.id;
            }
            var response = ModelService.createUpdateFluorochrome(instance);

            response.$promise.then(function () {
                // notify to update list
                ModelService.fluorochromesUpdated();

                // close modal
                $scope.ok();

            }, function (error) {
                $scope.errors = error.data;
            });
        };
    }
]);

app.controller(
    'SubjectGroupEditController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.current_project;

        $scope.create_update = function (instance) {
            $scope.errors = [];
            if (!instance.id) {
                instance.project = $scope.current_project.id;
            }

            var response = ModelService.createUpdateSubjectGroup(instance);

            response.$promise.then(function () {
                // notify to update list
                ModelService.subjectGroupsUpdated();

                // close modal
                $scope.ok();

            }, function (error) {
                $scope.errors = error.data;
            });
        };
    }
]);

app.controller(
    'SubjectEditController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.current_project;
        $scope.subject_groups = ModelService.getSubjectGroups(
            $scope.current_project.id
        );

        $scope.create_update = function (instance) {
            $scope.errors = [];
            if (!instance.id) {
                instance.project = $scope.current_project.id;
            }

            var response = ModelService.createUpdateSubject(instance);

            response.$promise.then(function () {
                // notify to update list
                ModelService.subjectsUpdated();

                // close modal
                $scope.ok();

            }, function (error) {
                $scope.errors = error.data;
            });
        };
    }
]);

app.controller(
    'SiteEditController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.current_project;

        $scope.create_update = function (instance) {
            $scope.errors = [];
            if (!instance.id) {
                instance.project = $scope.current_project.id;
            }

            var response = ModelService.createUpdateSite(instance);

            response.$promise.then(function () {
                // notify to update list
                ModelService.sitesUpdated();

                // close modal
                $scope.ok();

            }, function (error) {
                $scope.errors = error.data;
            });
        };
    }
]);

app.controller(
    'VisitTypeEditController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.current_project;

        $scope.create_update = function (instance) {
            $scope.errors = [];
            if (!instance.id) {
                instance.project = $scope.current_project.id;
            }

            var response = ModelService.createUpdateVisitType(instance);

            response.$promise.then(function () {
                // notify to update list
                ModelService.visitTypesUpdated();

                // close modal
                $scope.ok();

            }, function (error) {
                $scope.errors = error.data;
            });
        };
    }
]);

app.controller(
    'CellSubsetLabelEditController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.current_project;

        $scope.create_update = function (instance) {
            $scope.errors = [];
            if (!instance.id) {
                instance.project = $scope.current_project.id;
            }

            var response = ModelService.createUpdateCellSubsetLabel(instance);

            response.$promise.then(function () {
                // notify to update list
                ModelService.cellSubsetLabelsUpdated();

                // close modal
                $scope.ok();

            }, function (error) {
                $scope.errors = error.data;
            });
        };
    }
]);

app.controller(
    'StimulationEditController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.current_project;

        $scope.create_update = function (instance) {
            $scope.errors = [];
            if (!instance.id) {
                instance.project = $scope.current_project.id;
            }

            var response = ModelService.createUpdateStimulation(instance);

            response.$promise.then(function () {
                // notify to update list
                ModelService.stimulationsUpdated();

                // close modal
                $scope.ok();

            }, function (error) {
                $scope.errors = error.data;
            });
        };
    }
]);

app.controller(
    'PanelVariantEditController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.staining_types = ModelService.getStainingTypes();

        $scope.create_update = function (instance) {
            $scope.errors = [];

            var response = ModelService.createUpdatePanelVariant(instance);

            response.$promise.then(function () {
                // notify to update list
                ModelService.panelTemplatesUpdated();

                // close modal
                $scope.ok();

            }, function (error) {
                $scope.errors = error.data;
            });
        };
    }
]);

app.controller(
    'SampleEditController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.current_project = ModelService.current_project;

            $scope.subjects = ModelService.getSubjects(
                $scope.current_project.id
            );
            $scope.visit_types = ModelService.getVisitTypes(
                $scope.current_project.id
            );
            $scope.stimulations = ModelService.getStimulations(
                $scope.current_project.id
            );

            $scope.specimens = ModelService.getSpecimens();
            $scope.pretreatments = ModelService.getPretreatments();
            $scope.storages = ModelService.getStorages();

            $scope.update = function (instance) {
                $scope.errors = [];
                var response = ModelService.createUpdateSample(instance);

                response.$promise.then(function () {
                    // notify to update list
                    ModelService.samplesUpdated();

                    // close modal
                    $scope.ok();

                }, function (error) {
                    $scope.errors = error.data;
                });
            };
        }
    ]
);