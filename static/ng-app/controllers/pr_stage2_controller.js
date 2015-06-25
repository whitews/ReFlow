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
            $scope.instance.random_seed = 123;
            $scope.instance.subsample_count = 10000;
            $scope.instance.cell_subset = undefined;

            $scope.instance.invalid = true;

            $scope.check_inputs = function () {
                var invalid = false;
                var cluster_count = parseInt($scope.instance.cluster_count, 10);
                var burn_in_count = parseInt($scope.instance.burn_in_count, 10);
                var iteration_count = parseInt($scope.instance.iteration_count, 10);
                var random_seed = parseInt($scope.instance.random_seed, 10);
                var subsample_count = parseInt($scope.instance.subsample_count, 10);

                if (cluster_count % 1 !== 0) {
                    invalid = true;
                }
                if (burn_in_count % 1 !== 0) {
                    invalid = true;
                }
                if (iteration_count % 1 !== 0) {
                    invalid = true;
                }
                if (random_seed < 0 || random_seed > math.pow(2, 32) - 1) {
                    invalid = true;
                }
                if (subsample_count < 0 || subsample_count % 1 !== 0) {
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
                        subsample_count: $scope.instance.subsample_count,
                        cluster_count: $scope.instance.cluster_count,
                        burn_in_count: $scope.instance.burn_in_count,
                        iteration_count: $scope.instance.iteration_count,
                        random_seed: $scope.instance.random_seed,
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