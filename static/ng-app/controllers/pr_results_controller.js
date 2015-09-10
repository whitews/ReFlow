app.controller(
    'PRResultsController',
    [
        '$scope',
        '$q',
        '$controller',
        '$stateParams',
        '$window',
        'ModelService',
        function ($scope, $q, $controller, $stateParams, $window, ModelService) {
            // Inherits ProcessRequestController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.retrieving_data = true;
            $scope.samples = [];
            $scope.clusters = [];
            $scope.labels = [];
            $scope.filtered_results = [];
            var sample_lut = {};
            var label_lut = {};
            var sc_labels = [];

            $scope.filters = {};
            $scope.filters.selected_samples = [];
            $scope.filters.selected_clusters = [];
            $scope.filters.selected_labels = [];
            $scope.filters.min_event_percentage = null;
            $scope.filters.max_event_percentage = null;

            function create_results(sample_collection, sample_clusters) {
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

                $scope.labels.forEach(function (label) {
                    label_lut[label.id] = label.name;
                });

                $scope.clusters = [];

                sample_clusters.forEach(function(sc) {
                    if ($scope.clusters.indexOf(sc.cluster_index) == -1) {
                        $scope.clusters.push(sc.cluster_index);
                    }

                    sc_labels = [];
                    sc.labels.forEach(function (label_id) {
                        sc_labels.push(label_lut[label_id])
                    });

                    $scope.results.push(
                        {
                            'id': sc.sample,
                            'file_name': sample_lut[sc.sample],
                            'cluster_index': sc.cluster_index,
                            'event_percentage': sc.weight,
                            'labels': sc_labels
                        }
                    )
                });

                $scope.filtered_results = $scope.results;
                $scope.retrieving_data = false;
            }

            var r;  // each result when iterating during filtering

            $scope.apply_filter = function () {
                // filter results
                $scope.filtered_results = [];

                for (var i=0; i < $scope.results.length; i++) {

                    r = $scope.results[i];  // for easier reference

                    // match against selected samples
                    if ($scope.filters.selected_samples.length > 0) {
                        if ($scope.filters.selected_samples.indexOf(r.id) == -1) {
                            continue;
                        }
                    }
                    // match against min event_percentage
                    if ($scope.filters.min_event_percentage) {
                        if (parseFloat(r.event_percentage) < parseFloat($scope.filters.min_event_percentage)) {
                            continue;
                        }
                    }
                    // match against max event_percentage
                    if ($scope.filters.max_event_percentage) {
                        if (parseFloat(r.event_percentage) > parseFloat($scope.filters.max_event_percentage)) {
                            continue;
                        }
                    }
                    // match against selected clusters
                    if ($scope.filters.selected_clusters.length > 0) {
                        if ($scope.filters.selected_clusters.indexOf(r.cluster_index) == -1) {
                            continue;
                        }
                    }
                    // match against selected labels
                    if ($scope.filters.selected_labels.length > 0) {
                        var label_found = true;
                        $scope.filters.selected_labels.forEach(function (l) {
                            if (r.labels.indexOf(l) == -1) {
                                label_found = false;
                            }
                        });
                        if (!label_found) {
                            continue;
                        }
                    }

                    $scope.filtered_results.push(r);
                }
            };

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
                        data: angular.toJson($scope.filtered_results)
                    }
                );
                $window.location.assign("data:text/csv;charset=utf-8," + encodeURIComponent(exported_csv));
            };

            $scope.process_request = ModelService.getProcessRequest(
                $stateParams.requestId
            );
            $scope.labels = ModelService.getCellSubsetLabels(
                ModelService.current_project.id
            );

            $q.all([$scope.process_request.$promise, $scope.labels.$promise]).then(function () {
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