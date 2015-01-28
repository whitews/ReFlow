app.controller(
    'SpecimenController',
    [
        '$scope',
        '$controller',
        'ModelService',
        function ($scope, $controller, ModelService) {
            // Inherits MainController $scope
            $controller('MainController', {$scope: $scope});

            $scope.specimens = ModelService.getSpecimens();

            $scope.$on('specimens:updated', function () {
                $scope.specimens = ModelService.getSpecimens();
            });
        }
    ]
);

app.controller(
    'SpecimenEditController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.create_update = function (instance) {
                $scope.errors = [];
                var response = ModelService.createUpdateSpecimen(instance);

                response.$promise.then(function () {
                    // notify to update list
                    ModelService.specimensUpdated();

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
    'SpecimenDeleteController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.destroy = function (instance) {
                var response = ModelService.destroySpecimen(instance);

                response.$promise.then(function () {
                    // notify to update list
                    ModelService.specimensUpdated();

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
    'MarkerController',
    [
        '$scope',
        '$controller',
        'ModelService',
        function ($scope, $controller, ModelService) {
            // Inherits MainController $scope
            $controller('MainController', {$scope: $scope});

            $scope.markers = ModelService.getMarkers();

            $scope.$on('markers:updated', function () {
                $scope.markers = ModelService.getMarkers();
            });
        }
    ]
);

app.controller(
    'MarkerEditController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.create_update = function (instance) {
                $scope.errors = [];
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
    'FluorochromeController',
    [
        '$scope',
        '$controller',
        'ModelService',
        function ($scope, $controller, ModelService) {
            // Inherits MainController $scope
            $controller('MainController', {$scope: $scope});

            $scope.fluorochromes = ModelService.getFluorochromes();

            $scope.$on('fluorochromes:updated', function () {
                $scope.fluorochromes = ModelService.getFluorochromes();
            });
        }
    ]
);

app.controller(
    'FluorochromeEditController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.create_update = function (instance) {
                $scope.errors = [];
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
    'UserController',
    [
        '$scope',
        '$controller',
        'ModelService',
        function ($scope, $controller, ModelService) {
            // Inherits MainController $scope
            $controller('MainController', {$scope: $scope});

            $scope.users = ModelService.getUsers();

            $scope.$on('users:updated', function () {
                $scope.users = ModelService.getUsers();
            });
        }
    ]
);

app.controller(
    'UserEditController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.create_update = function (instance) {
                $scope.errors = [];
                var response = ModelService.createUpdateUser(instance);

                response.$promise.then(function () {
                    // notify to update list
                    ModelService.usersUpdated();

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
    'UserDeleteController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.destroy = function (instance) {
                var response = ModelService.destroyUser(instance);

                response.$promise.then(function () {
                    // notify to update list
                    ModelService.usersUpdated();

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
    'WorkerController',
    [
        '$scope',
        '$controller',
        'ModelService',
        function ($scope, $controller, ModelService) {
            // Inherits MainController $scope
            $controller('MainController', {$scope: $scope});

            $scope.workers = ModelService.getWorkers();

            $scope.$on('workers:updated', function () {
                $scope.workers = ModelService.getWorkers();
            });
        }
    ]
);

app.controller(
    'WorkerEditController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.create_update = function (instance) {
                $scope.errors = [];
                var response = ModelService.createUpdateWorker(instance);

                response.$promise.then(function () {
                    // notify to update list
                    ModelService.workersUpdated();

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
    'WorkerDeleteController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.destroy = function (instance) {
                var response = ModelService.destroyWorker(instance);

                response.$promise.then(function () {
                    // notify to update list
                    ModelService.workersUpdated();

                    // close modal
                    $scope.ok();

                }, function (error) {
                    $scope.errors = error.data;
                });
            };
        }
    ]
);