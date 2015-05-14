app.controller(
    'PRStage2Controller',
    [
        '$scope',
        '$controller',
        'ModelService',
        function ($scope, $controller, ModelService) {
            // PRVisualizationController pushes necessary vars through to this
            // controller

            console.log();

            $scope.submit_request = function () {
                var second_stage_clusters = [];
                var second_stage_params = [];

                $scope.instance.clusters.forEach(function (c) {
                    if (c.labels.indexOf($scope.instance.cell_subset.id.toString()) != -1) {
                        second_stage_clusters.push(c.cluster);
                    }
                });

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
                        clusters: second_stage_clusters,
                        parameters: second_stage_params
                    }
                );
                pr.$promise.then(function () {

                });
            };
        }
    ]
);