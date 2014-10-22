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
                );

                $scope.sample_clusters.$promise.then(function() {
                     ModelService.getSampleCSV($scope.chosen_sample_id)
                        .success(function (data, status, headers) {
                            $scope.plot_data = {
                                'cluster_data': $scope.sample_clusters,
                                'event_data': data
                            };
                             $scope.retrieving_data = false;
                        }).error(function (data, status, headers, config) {
                            $scope.event_data = -1;
                            $scope.retrieving_data = false;
                        });
                });
            }
        }
    ]
);