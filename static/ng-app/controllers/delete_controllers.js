app.controller(
    'SampleDeleteController',
    [
        '$scope',
        '$rootScope',
        '$controller',
        'Sample',
        function ($scope, $rootScope, $controller, Sample) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.destroy = function (instance) {
                $scope.errors = [];
                var response;
                response = Sample.delete({id: instance.id });

                response.$promise.then(function () {
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
    'BeadSampleDeleteController',
    [
        '$scope',
        '$rootScope',
        '$controller',
        'BeadSample',
        function ($scope, $rootScope, $controller, BeadSample) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.destroy = function (instance) {
                $scope.errors = [];
                var response;
                response = BeadSample.delete({id: instance.id });

                response.$promise.then(function () {
                    $rootScope.$broadcast('updateBeadSamples');

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
    'CompensationDeleteController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.destroy = function (instance) {
                var response = ModelService.destroyCompensation(instance);

                response.$promise.then(function () {
                    // notify to update comp list
                    ModelService.compensationsUpdated();

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
                $scope.errors = ModelService.destroyCytometer(instance);

                if (!$scope.errors) {
                    $scope.ok();
                }
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
                $scope.errors = ModelService.destroyStimulation(instance);

                if (!$scope.errors) {
                    $scope.ok();
                }
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
                $scope.errors = ModelService.destroyVisitType(instance);

                if (!$scope.errors) {
                    $scope.ok();
                }
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
                $scope.errors = ModelService.destroySite(instance);

                if (!$scope.errors) {
                    $scope.ok();
                }
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
                $scope.errors = ModelService.destroyPanelTemplate(instance);

                if (!$scope.errors) {
                    $scope.ok();
                }
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
                $scope.errors = ModelService.destroySubject(instance);

                if (!$scope.errors) {
                    $scope.ok();
                }
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
    'ProjectDeleteController',
    [
        '$scope',
        '$rootScope',
        '$controller',
        '$state',
        'Project',
        function ($scope, $rootScope, $controller, $state, Project) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            // refresh project so user sees the any recent changes
            $scope.instance = Project.get({id: $scope.instance.id});

            $scope.destroy = function (instance) {
                $scope.errors = [];
                var response;
                response = Project.delete({id: instance.id });

                response.$promise.then(function () {
                    $rootScope.$broadcast('updateProjects');

                    // close modal
                    $scope.ok();

                    $state.go('home');

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
        '$rootScope',
        '$controller',
        'ProcessRequest',
        function ($scope, $rootScope, $controller, ProcessRequest) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.destroy = function (instance) {
                $scope.errors = [];
                var response;
                response = ProcessRequest.delete({id: instance.id });

                response.$promise.then(function () {
                    $rootScope.$broadcast('updateProcessRequests');

                    // close modal
                    $scope.ok();

                }, function (error) {
                    $scope.errors = error.data;
                });
            };
        }
    ]
);