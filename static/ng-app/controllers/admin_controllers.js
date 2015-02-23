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