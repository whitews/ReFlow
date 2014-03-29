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
        'ProjectPanel',
        'SitePanel',
        function ($scope, $modal, Project, Site, ProjectPanel, SitePanel) {

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

            $scope.model = {
                projects: Project.query(),
                current_project: null,
                project_panels: null,
                current_project_panel: null,
                sites: null,
                site_panels: null
            };

            function preselectSites() {
                $scope.model.sites.forEach(function(site) {
                    site.selected = true;
                });
            }

            $scope.projectChanged = function () {
                $scope.model.project_panels = ProjectPanel.query({project: $scope.model.current_project.id});
                $scope.model.sites = Site.query({project: $scope.model.current_project.id});
                preselectSites();
            };

            $scope.updateSitePanels = function () {
                var site_id_list = [];
                $scope.model.sites.forEach(function(site) {
                    if (site.selected) {
                        site_id_list.push(site.id);
                    }
                });

                if (site_id_list == 0) {
                    $scope.model.site_panels = null;
                } else {
                    $scope.model.site_panels = SitePanel.query(
                    {
                        project_panel: $scope.model.current_project_panel.id,
                        site: site_id_list
                    });
                }
            };

            $scope.toggleAllSitePanels = function () {
                $scope.model.site_panels.forEach(function(site_panel) {
                    site_panel.selected = $scope.model.master_site_panel_checkbox;
                });
            };


        }
    ]
);