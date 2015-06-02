app.controller(
    'ProjectDeleteController',
    [
        '$scope',
        '$state',
        'ModelService',
        function ($scope, $state, ModelService) {
            $scope.destroy = function (instance) {
                var response = ModelService.destroyProject(instance);

                response.$promise.then(function () {
                    // notify to update list
                    ModelService.projectsUpdated();

                    // close modal
                    $scope.ok();

                    // can only delete project while browsing it, so re-route
                    $state.go('home');
                }, function (error) {
                    $scope.errors = error.data;
                });
            }
        }
    ]
);

app.controller(
    'MarkerDeleteController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.destroy = function (instance) {
                var response = ModelService.destroyMarker(instance);

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
    ]
);

app.controller(
    'FluorochromeDeleteController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.destroy = function (instance) {
                var response = ModelService.destroyFluorochrome(instance);

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
    ]
);

app.controller(
    'SampleDeleteController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.destroy = function (instance) {
                $scope.errors = [];
                var response;
                response = ModelService.destroySample(instance);

                response.$promise.then(function () {
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

app.controller(
    'CytometerDeleteController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.destroy = function (instance) {
                var response = ModelService.destroyCytometer(instance);

                response.$promise.then(function () {
                    // notify to update list
                    ModelService.cytometersUpdated();

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
    'StimulationDeleteController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.destroy = function (instance) {
                var response = ModelService.destroyStimulation(instance);

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
    ]
);

app.controller(
    'VisitTypeDeleteController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.destroy = function (instance) {
                var response = ModelService.destroyVisitType(instance);

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
    ]
);

app.controller(
    'SiteDeleteController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.destroy = function (instance) {
                var response = ModelService.destroySite(instance);

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
    ]
);

app.controller(
    'PanelTemplateDeleteController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.destroy = function (instance) {
                var response = ModelService.destroyPanelTemplate(instance);

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
    ]
);

app.controller(
    'PanelVariantDeleteController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.destroy = function (instance) {
                var response = ModelService.destroyPanelVariant(instance);

                response.$promise.then(function () {
                    // notify to update panel template list
                    ModelService.panelTemplatesUpdated();

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
    'SitePanelDeleteController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.destroy = function (instance) {
                var response = ModelService.destroySitePanel(instance);

                response.$promise.then(function () {
                    // notify to update list
                    ModelService.sitePanelsUpdated();

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
    'SubjectDeleteController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.destroy = function (instance) {
                var response = ModelService.destroySubject(instance);

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
    ]
);

app.controller(
    'SubjectGroupDeleteController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.destroy = function (instance) {
                var response = ModelService.destroySubjectGroup(instance);

                response.$promise.then(function () {
                    // notify to update list
                    ModelService.subjectGroupsUpdated();

                    // close modal
                    $scope.ok();

                }, function (error) {
                    $scope.errors = error.data;
                });
            }
        }
    ]
);

app.controller(
    'CellSubsetLabelDeleteController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.destroy = function (instance) {
                var response = ModelService.destroyCellSubsetLabel(instance);

                response.$promise.then(function () {
                    // notify to update comp list
                    ModelService.cellSubsetLabelsUpdated();

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
    'ProcessRequestDeleteController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.destroy = function (instance) {
                $scope.errors = [];
                var response;
                response = ModelService.destroyProcessRequest(instance);

                response.$promise.then(function () {
                    ModelService.processRequestsUpdated();

                    // close modal
                    $scope.ok();

                }, function (error) {
                    $scope.errors = error.data;
                });
            };
        }
    ]
);