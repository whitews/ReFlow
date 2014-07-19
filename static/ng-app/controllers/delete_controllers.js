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
        '$rootScope',
        '$controller',
        'Compensation',
        function ($scope, $rootScope, $controller, Compensation) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.destroy = function (instance) {
                $scope.errors = [];
                var response;
                response = Compensation.delete({id: instance.id });

                response.$promise.then(function () {
                    $rootScope.$broadcast('updateCompensations');

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
        '$rootScope',
        '$controller',
        'Cytometer',
        function ($scope, $rootScope, $controller, Cytometer) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.destroy = function (instance) {
                $scope.errors = [];
                var response;
                response = Cytometer.delete({id: instance.id });

                response.$promise.then(function () {
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
    'StimulationDeleteController',
    [
        '$scope',
        '$rootScope',
        '$controller',
        'Stimulation',
        function ($scope, $rootScope, $controller, Stimulation) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.destroy = function (instance) {
                $scope.errors = [];
                var response;
                response = Stimulation.delete({id: instance.id });

                response.$promise.then(function () {
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
    'VisitTypeDeleteController',
    [
        '$scope',
        '$rootScope',
        '$controller',
        'VisitType',
        function ($scope, $rootScope, $controller, VisitType) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.destroy = function (instance) {
                $scope.errors = [];
                var response;
                response = VisitType.delete({id: instance.id });

                response.$promise.then(function () {
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
    'SiteDeleteController',
    [
        '$scope',
        '$rootScope',
        '$controller',
        'Site',
        function ($scope, $rootScope, $controller, Site) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.destroy = function (instance) {
                $scope.errors = [];
                var response;
                response = Site.delete({id: instance.id });

                response.$promise.then(function () {
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
    'PanelTemplateDeleteController',
    [
        '$scope',
        '$rootScope',
        '$controller',
        'PanelTemplate',
        function ($scope, $rootScope, $controller, PanelTemplate) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.destroy = function (instance) {
                $scope.errors = [];
                var response;
                response = PanelTemplate.delete({id: instance.id });

                response.$promise.then(function () {
                    $rootScope.$broadcast('updatePanelTemplates');

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
        '$rootScope',
        '$controller',
        'Subject',
        function ($scope, $rootScope, $controller, Subject) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.destroy = function (instance) {
                $scope.errors = [];
                var response;
                response = Subject.delete({id: instance.id });

                response.$promise.then(function () {
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
    'SubjectGroupDeleteController',
    [
        '$scope',
        '$rootScope',
        '$controller',
        'SubjectGroup',
        function ($scope, $rootScope, $controller, SubjectGroup) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.destroy = function (instance) {
                $scope.errors = [];
                var response;
                response = SubjectGroup.delete({id: instance.id });

                response.$promise.then(function () {
                    $rootScope.$broadcast('updateSubjectGroups');

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