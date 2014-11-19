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
                $scope.sample_collection = ModelService.getSampleCollection(
                    $scope.process_request.sample_collection
                )
            });
        }
    ]
);