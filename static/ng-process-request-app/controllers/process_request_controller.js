/**
 * Created by swhite on 2/25/14.
 */

var process_steps = [
    {
        "name": "filter_site_panels",
        "title": "Choose Site Panels",
        "url": "/static/ng-process-request-app/partials/choose_site_panels.html"
    },
    {
        "name": "filter_samples",
        "title": "Choose Samples",
        "url": "/static/ng-process-request-app/partials/choose_samples.html"
    },
    {
        "name": "filter_parameters",
        "title": "Choose Parameters",
        "url": "/static/ng-process-request-app/partials/choose_parameters.html"
    },
    {
        "name": "choose_clustering",
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
        'Sample',
        'Subject',
        'VisitType',
        'Stimulation',
        'Cytometer',
        'Pretreatment',
        function ($scope, $modal, Project, Site, ProjectPanel, SitePanel, Sample, Subject, VisitType, Stimulation, Cytometer, Pretreatment) {

            $scope.current_step_index = 0;
            $scope.step_count = process_steps.length;
            $scope.current_step = process_steps[$scope.current_step_index];

            function initializeSamples () {
                var site_panel_list = [];
                $scope.model.site_panels.forEach(function(site_panel) {
                    if (site_panel.selected) {
                        site_panel_list.push(site_panel.id);
                    }
                });

                if (site_panel_list == 0) {
                    $scope.model.site_panels = null;
                } else {
                    $scope.model.samples = Sample.query({site_panel: site_panel_list});
                }

                var site_list = [];
                $scope.model.sites.forEach(function(site) {
                    if (site.selected) {
                        site_list.push(site.id);
                    }
                });

                $scope.model.subjects = Subject.query({project: $scope.model.current_project.id});
                $scope.model.visits = VisitType.query({project: $scope.model.current_project.id});
                $scope.model.stimulations = Stimulation.query({project: $scope.model.current_project.id});
                $scope.model.cytometers = Cytometer.query({site: site_list});
                $scope.model.pretreatments = Pretreatment.query();

            }

            function initializeStep () {
                switch ($scope.current_step.name) {
                    case "filter_site_panels":
                        // Nothing to do here
                        break;
                    case "filter_samples":
                        initializeSamples();
                        break;
                    case "filter_parameters":
                        initializeParameters();
                        break;
                    case "choose_clustering":
                        initializeClustering();
                        break;
                }
            }

            $scope.nextStep = function () {
                if ($scope.current_step_index < process_steps.length - 1) {
                    $scope.current_step_index++;
                    $scope.current_step = process_steps[$scope.current_step_index];
                    initializeStep();
                }
            };
            $scope.prevStep = function () {
                if ($scope.current_step_index > 0) {
                    $scope.current_step_index--;
                    $scope.current_step = process_steps[$scope.current_step_index];
                    initializeStep();
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