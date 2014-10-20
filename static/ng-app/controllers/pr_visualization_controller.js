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
            $scope.chosen_sample_id = null;

            $scope.process_request = ModelService.getProcessRequest(
                $stateParams.requestId
            );

            $scope.process_request.$promise.then(function () {
                $scope.sample_collection = ModelService.getSampleCollectionMembers(
                    $scope.process_request.sample_collection
                )
            });

            $scope.$watch('chosen_sample_id', function() {
                if ($scope.chosen_sample_id) {
                    $scope.retrieving_data = true;
                    initialize_plot();
                }
            });

            function initialize_plot() {
                $scope.sample_clusters = ModelService.getSampleClusters(
                    $scope.process_request.id,
                    $scope.chosen_sample_id
                )

                $scope.sample_clusters.$promise.then(function() {
                    $scope.retrieving_data = false;
                });
            }
        }
    ]
);