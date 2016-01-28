app.controller(
    'PRSingleLabelController',
    [
        '$scope',
        '$controller',
        'ModelService',
        function ($scope) {
            // PRVisualizationController pushes necessary vars through to this
            // controller

            // some input defaults
            $scope.instance.cell_subset = undefined;

            $scope.instance.invalid = true;

            $scope.check_inputs = function () {
                var invalid = false;

                if ($scope.instance.cell_subset === undefined) {
                    invalid = true;
                }

                $scope.instance.invalid = invalid;
            };

            $scope.apply_labels = function () {
                $scope.instance.add_cluster_label(
                    $scope.instance.cell_subset,
                    $scope.instance.cluster
                );
                // close modal
                $scope.ok();
            };
        }
    ]
);

app.controller(
    'PRMultiLabelController',
    [
        '$scope',
        '$controller',
        'ModelService',
        function ($scope) {
            // PRVisualizationController pushes necessary vars through to this
            // controller

            // some input defaults
            $scope.instance.cell_subset = undefined;

            $scope.instance.invalid = true;

            $scope.check_inputs = function () {
                var invalid = false;

                if ($scope.instance.cell_subset === undefined) {
                    invalid = true;
                }

                $scope.instance.invalid = invalid;
            };

            $scope.apply_labels = function () {
                $scope.instance.clusters.forEach(function(c) {
                    if (c.display_events === true) {
                        // check if cluster already has this label
                        var skip_cluster = false;
                        for (var i = 0; i < c.labels.length; i++) {
                            if (c.labels[i].label === $scope.instance.cell_subset.id) {
                                skip_cluster = true;
                                break;
                            }
                        }

                        if (!skip_cluster) {
                            $scope.instance.add_cluster_label(
                                $scope.instance.cell_subset,
                                c
                            );
                        }
                    }
                });
                // close modal
                $scope.ok();
            };
        }
    ]
);