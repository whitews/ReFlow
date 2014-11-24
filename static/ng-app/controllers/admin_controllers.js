app.controller(
    'AdminController',
    ['$scope', '$modal', function ($scope, $modal) {
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
]);

app.controller(
    'SpecimenController',
    [
        '$scope',
        '$controller',
        '$modal',
        'Specimen',
        function ($scope, $controller, $modal, Specimen) {
            // Inherits MainController $scope
            $controller('MainController', {$scope: $scope});

            function get_list() {
                return Specimen.query(
                    {}
                );
            }
            $scope.specimens = get_list();

            $scope.$on('updateSpecimens', function () {
                $scope.specimens = get_list();
            });

            $scope.init_form = function(instance) {
                var proposed_instance = angular.copy(instance);
                $scope.errors = [];

                // launch form modal
                var modalInstance = $modal.open({
                    templateUrl: MODAL_URLS.SPECIMEN,
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
    'SpecimenEditController',
    [
        '$scope',
        '$rootScope',
        '$controller',
        'Specimen',
        function ($scope, $rootScope, $controller, Specimen) {
            // Inherits SpecimenController $scope
            $controller('SpecimenController', {$scope: $scope});

            $scope.create_update = function (instance) {
                $scope.errors = [];
                var response;
                if (instance.id) {
                    response = Specimen.update(
                        {id: instance.id },
                        $scope.instance
                    );
                } else {
                    response = Specimen.save(
                        $scope.instance
                    );
                }

                response.$promise.then(function () {
                    // notify to update subject list
                    $rootScope.$broadcast('updateSpecimens');

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
        '$modal',
        'Marker',
        function ($scope, $controller, $modal, Marker) {
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

            $scope.init_form = function(instance) {
                var proposed_instance = angular.copy(instance);
                $scope.errors = [];

                // launch form modal
                var modalInstance = $modal.open({
                    templateUrl: MODAL_URLS.MARKER,
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
        '$modal',
        'Fluorochrome',
        function ($scope, $controller, $modal, Fluorochrome) {
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

            $scope.init_form = function(instance) {
                var proposed_instance = angular.copy(instance);
                $scope.errors = [];

                // launch form modal
                var modalInstance = $modal.open({
                    templateUrl: MODAL_URLS.FLUOROCHROME,
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
        '$modal',
        'Worker',
        function ($scope, $controller, $modal, Worker) {
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

            $scope.init_form = function(instance) {
                var proposed_instance = angular.copy(instance);
                $scope.errors = [];

                // launch form modal
                var modalInstance = $modal.open({
                    templateUrl: MODAL_URLS.WORKER,
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