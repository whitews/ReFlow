app.controller(
    'PRVisualizationController',
    [
        '$scope',
        '$controller',
        '$stateParams',
        'ModelService',
        function ($scope, $controller, $stateParams, ModelService) {
            // Inherits ProcessRequestController $scope
            $controller('ProcessRequestController', {$scope: $scope});

            $scope.process_request = ModelService.getProcessRequest(
                $stateParams.requestId
            );
        }
    ]
);