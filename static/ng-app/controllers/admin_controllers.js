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
        'Marker',
        function ($scope, $controller, Marker) {
            // Inherits MainController $scope
            $controller('MainController', {$scope: $scope});

            function get_list() {
                return Marker.query(
                    {}
                );
            }
            $scope.markers = get_list();

            $scope.$on('updateMarkers', function () {
                $scope.markers = get_list();
            });
        }
    ]
);

app.controller(
    'MarkerEditController',
    [
        '$scope',
        '$rootScope',
        '$controller',
        'Marker',
        function ($scope, $rootScope, $controller, Marker) {
            // Inherits MarkerController $scope
            $controller('MarkerController', {$scope: $scope});

            $scope.create_update = function (instance) {
                $scope.errors = [];
                var response;
                if (instance.id) {
                    response = Marker.update(
                        {id: instance.id },
                        $scope.instance
                    );
                } else {
                    response = Marker.save(
                        $scope.instance
                    );
                }

                response.$promise.then(function () {
                    // notify to update subject list
                    $rootScope.$broadcast('updateMarkers');

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
        'Fluorochrome',
        function ($scope, $controller, Fluorochrome) {
            // Inherits MainController $scope
            $controller('MainController', {$scope: $scope});

            function get_list() {
                return Fluorochrome.query(
                    {}
                );
            }
            $scope.fluorochromes = get_list();

            $scope.$on('updateFluorochromes', function () {
                $scope.fluorochromes = get_list();
            });
        }
    ]
);

app.controller(
    'FluorochromeEditController',
    [
        '$scope',
        '$rootScope',
        '$controller',
        'Fluorochrome',
        function ($scope, $rootScope, $controller, Fluorochrome) {
            // Inherits FluorochromeController $scope
            $controller('FluorochromeController', {$scope: $scope});

            $scope.create_update = function (instance) {
                $scope.errors = [];
                var response;
                if (instance.id) {
                    response = Fluorochrome.update(
                        {id: instance.id },
                        $scope.instance
                    );
                } else {
                    response = Fluorochrome.save(
                        $scope.instance
                    );
                }

                response.$promise.then(function () {
                    // notify to update subject list
                    $rootScope.$broadcast('updateFluorochromes');

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
        'Worker',
        function ($scope, $controller, Worker) {
            // Inherits MainController $scope
            $controller('MainController', {$scope: $scope});

            function get_list() {
                return Worker.query(
                    {}
                );
            }
            $scope.workers = get_list();

            $scope.$on('updateWorkers', function () {
                $scope.workers = get_list();
            });
        }
    ]
);

app.controller(
    'WorkerEditController',
    [
        '$scope',
        '$rootScope',
        '$controller',
        'Worker',
        function ($scope, $rootScope, $controller, Worker) {
            // Inherits WorkerController $scope
            $controller('WorkerController', {$scope: $scope});

            $scope.create_update = function (instance) {
                $scope.errors = [];
                var response;
                if (instance.id) {
                    response = Worker.update(
                        {id: instance.id },
                        $scope.instance
                    );
                } else {
                    response = Worker.save(
                        $scope.instance
                    );
                }

                response.$promise.then(function () {
                    // notify to update subject list
                    $rootScope.$broadcast('updateWorkers');

                    // close modal
                    $scope.ok();

                }, function (error) {
                    $scope.errors = error.data;
                });
            };
        }
    ]
);