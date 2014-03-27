/**
 * Created by swhite on 2/25/14.
 */

var process_steps = [
    {
        "title": "Choose Site Panels",
        "url": "/static/ng-process-request-app/partials/choose_site_panels.html"
    },
    {
        "title": "Choose Samples",
        "url": "/static/ng-process-request-app/partials/choose_samples.html"
    },
    {
        "title": "Choose Parameters",
        "url": "/static/ng-process-request-app/partials/choose_parameters.html"
    },
    {
        "title": "Clustering Options",
        "url": "/static/ng-process-request-app/partials/choose_clustering.html"
    }
];

app.controller(
    'ProcessRequestController',
    [
        '$scope',
        '$modal',
        'Project',
        'Site',
        function ($scope, $modal, Project, Site) {

            $scope.current_step_index = 0;
            $scope.step_count = process_steps.length;
            $scope.current_step = process_steps[$scope.current_step_index];

            $scope.nextStep = function () {
                if ($scope.current_step_index < process_steps.length - 1) {
                    $scope.current_step_index++;
                    $scope.current_step = process_steps[$scope.current_step_index];
                }
            };
            $scope.prevStep = function () {
                if ($scope.current_step_index > 0) {
                    $scope.current_step_index--;
                    $scope.current_step = process_steps[$scope.current_step_index];
                }
            };

            $scope.projects = Project.query();

            $scope.projectChanged = function () {
                $scope.sites = Site.query({project: this.current_project.id});
            };


        }
    ]
);