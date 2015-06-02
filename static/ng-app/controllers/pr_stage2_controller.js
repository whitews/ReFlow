app.controller(
    'PRStage2Controller',
    [
        '$scope',
        '$controller',
        'ModelService',
        function ($scope, $controller, ModelService) {
            // PRVisualizationController pushes necessary vars through to this
            // controller

            // some input defaults
            $scope.instance.cluster_count = 32;
            $scope.instance.burn_in_count = 5000;
            $scope.instance.iteration_count = 50;
            $scope.instance.cell_subset = undefined;

            $scope.instance.invalid = true;

            $scope.check_inputs = function () {
                var invalid = false;

                if ($scope.instance.cluster_count % 1 !== 0) {
                    invalid = true;
                }
                if ($scope.instance.burn_in_count % 1 !== 0) {
                    invalid = true;
                }
                if ($scope.instance.iteration_count % 1 !== 0) {
                    invalid = true;
                }
                if ($scope.instance.cell_subset === undefined) {
                    invalid = true;
                }

                var selected_params = 0;
                $scope.instance.parameters.forEach(function (p) {
                    if (p.selected) {
                        selected_params++;
                    }
                });
                if (selected_params <= 0) {
                    invalid = true;
                }

                $scope.instance.invalid = invalid;
            };

            $scope.submit_request = function () {
                var second_stage_params = [];

                $scope.instance.parameters.forEach(function (p) {
                    if (p.selected) {
                        second_stage_params.push(p.full_name_underscored);
                    }
                });

                var pr = ModelService.createProcessRequestStage2(
                    {
                        parent_pr_id: $scope.instance.parent_pr_id,
                        description: $scope.instance.cell_subset.name,
                        // hard-coding 10k sub-samples for now
                        // TODO: allow user to specify subsample_count
                        subsample_count: 10000,
                        cluster_count: $scope.instance.cluster_count,
                        burn_in_count: $scope.instance.burn_in_count,
                        iteration_count: $scope.instance.iteration_count,
                        cell_subset_label: $scope.instance.cell_subset.id,
                        parameters: second_stage_params
                    }
                );
                pr.$promise.then(function () {
                    // close modal
                    $scope.ok();
                }, function (error) {
                    $scope.errors = error.data;
                });
            };
        }
    ]
);