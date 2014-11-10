app.controller(
    'PRVisualizationController',
    [
        '$scope',
        '$q',
        '$controller',
        '$stateParams',
        'ModelService',
        function ($scope, $q, $controller, $stateParams, ModelService) {
            // Inherits ProcessRequestController $scope
            $controller('ProcessRequestController', {$scope: $scope});
            $scope.chosen_member_index = null;
            var chosen_member = null;
            var sample_clusters = null;
            var panel_data = null;
            var event_data = null;

            $scope.process_request = ModelService.getProcessRequest(
                $stateParams.requestId
            );

            $scope.process_request.$promise.then(function () {
                $scope.sample_collection = ModelService.getSampleCollection(
                    $scope.process_request.sample_collection
                )
            });

            $scope.$watch('chosen_member_index', function() {
                if ($scope.chosen_member_index !== null) {
                    $scope.retrieving_data = true;
                    chosen_member = $scope.sample_collection.members[parseInt($scope.chosen_member_index)];
                    initialize_plot();
                }
            });

            function initialize_plot() {
                sample_clusters = ModelService.getSampleClusters(
                    $scope.process_request.id,
                    chosen_member.sample.id
                );

                panel_data = ModelService.getSitePanel(
                    chosen_member.sample.site_panel
                );

                event_data = ModelService.getSampleCSV(
                    chosen_member.sample.id
                );

                $q.all([sample_clusters, panel_data, event_data]).then(function(data) {
                    $scope.plot_data = {
                        'cluster_data': data[0],
                        'panel_data': data[1],
                        'event_data': data[2].data,
                        'compensation_data': chosen_member.compensation
                    };
                }).catch(function() {
                    // show errors here
                    console.log('error!')
                }).finally(function() {
                    $scope.retrieving_data = false;
                });
            }
        }
    ]
);