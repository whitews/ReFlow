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