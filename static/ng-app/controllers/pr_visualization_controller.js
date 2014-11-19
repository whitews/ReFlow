app.controller(
    'PRVisualizationDetailController',
    [
        '$scope',
        '$q',
        '$controller',
        '$stateParams',
        'ModelService',
        function ($scope, $q, $controller, $stateParams, ModelService) {
            // Inherits ProcessRequestController $scope
            $controller('ProcessRequestController', {$scope: $scope});

            $scope.process_request = ModelService.getProcessRequest(
                $stateParams.requestId
            );

            $scope.process_request.$promise.then(function () {
                ModelService.getSampleCollection(
                    $scope.process_request.sample_collection
                ).$promise.then(function (data) {
                    $scope.sample_collection = data;
                });
            });
        }
    ]
);