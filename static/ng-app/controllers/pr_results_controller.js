app.controller(
    'PRResultsController',
    [
        '$scope',
        '$stateParams',
        '$window',
        'ModelService',
        function ($scope, $stateParams, $window, ModelService) {
            $scope.selected_samples = [];
            $scope.samples = [];

            function create_results(sample_collection, sample_clusters) {
                var sample_lut = {};

                $scope.results = [];
                sample_collection.members.forEach(function (member) {
                    sample_lut[member.sample.id] = member.sample.original_filename;

                    $scope.samples.push(
                        {
                            'id': member.sample.id,
                            'filename': member.sample.original_filename
                        }
                    );
                });

                sample_clusters.forEach(function(sc) {
                    $scope.results.push(
                        {
                            'file_name': sample_lut[sc.sample],
                            'cluster_index': sc.cluster_index,
                            'weight': sc.weight,
                            'labels': sc.labels
                        }
                    )
                });
            }

            $scope.create_export = function () {
                // use angular.toJson, removes ng internal props like $$hashkey
                var exported_csv = Papa.unparse(
                    {
                        fields: [
                            "file_name",
                            "cluster_index",
                            "event_percentage",
                            "labels"
                        ],
                        data: angular.toJson($scope.$parent.filtered_results)
                    }
                );
                $window.location.assign("data:text/csv;charset=utf-8," + encodeURIComponent(exported_csv));
            };

            $scope.process_request = ModelService.getProcessRequest(
                $stateParams.requestId
            );

            $scope.process_request.$promise.then(function (pr) {
                // get sample collection for this PR
                ModelService.getSampleCollection(
                    $scope.process_request.sample_collection
                ).$promise.then(function (sample_collection) {
                    ModelService.getSampleClusters(
                        $scope.process_request.id
                    ).then(function (sample_clusters) {
                        create_results(sample_collection, sample_clusters);
                    });
                });
            });
        }
    ]
);