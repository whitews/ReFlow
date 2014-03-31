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
                    $scope.model.samples = null;
                } else {
                    $scope.model.samples = Sample.query(
                        {site_panel: site_panel_list},
                        function (data) {  // success
                            data.forEach(function (sample) {
                                sample.ignore = false;
                                sample.selected = true;
                            });
                        }
                    );
                }

                // Add ignore=false, selected=true to all samples
                $scope.model.samples.forEach(function (sample) {
                    sample.ignore = false;
                    sample.selected = true;
                });

                var site_list = [];
                $scope.model.sites.forEach(function(site) {
                    if (site.selected) {
                        site_list.push(site.id);
                    }
                });

                // Populate our sample filters
                $scope.model.subjects = Subject.query({project: $scope.model.current_project.id});
                $scope.model.visits = VisitType.query({project: $scope.model.current_project.id});
                $scope.model.stimulations = Stimulation.query({project: $scope.model.current_project.id});
                $scope.model.cytometers = Cytometer.query({site: site_list});
                $scope.model.pretreatments = Pretreatment.query();

            }

            function initializeParameters () {
                // Iterate samples that are both selected and not ignored
                // to collect distinct site panels
                // Then iterate over site panels to get the intersection
                // of parameters
                var site_panel_list = [];
                $scope.model.samples.forEach(function (sample) {
                    if (sample.selected && !sample.ignore) {
                        if (site_panel_list.indexOf(sample.site_panel) == -1) {
                            site_panel_list.push(sample.site_panel);
                        }
                    }
                });

                // For the parameter list, we'll start by adding all the
                // params from the first site panel we encounter
                // and if a subsequent site panel doesn't contain a
                // parameter we remove it from the list. At the end,
                // we should have the intersection of parameters
                var master_parameter_list = [];
                var panel_match_count = 0;
                $scope.model.site_panels.forEach (function (site_panel) {
                    var parameter_list = [];
                    if (site_panel_list.indexOf(site_panel.id) != -1) {
                        site_panel.parameters.forEach(function (parameter) {
                            // since multiple markers are possible in a param
                            // we'll get those first, sorted alphabetically
                            var marker_list = [];
                            var marker_string = null;
                            parameter.markers.forEach(function (marker) {
                                marker_list.push(marker.name);
                            });
                            if (marker_list.length > 0) {
                                marker_string = marker_list.sort().join('_');
                            }
                            var param_string = parameter.parameter_type + "_" +
                                parameter.parameter_value_type + "_";
                            if (marker_string) {
                                param_string = param_string + marker_string + "_";
                            }
                            if (parameter.fluorochrome) {
                                param_string = param_string + parameter.fluorochrome.fluorochrome_abbreviation;
                            }
                            parameter_list.push(param_string);
                        });

                        // if it's our first rodeo save to master list
                        if (panel_match_count == 0) {
                            parameter_list.forEach(function (p) {
                                master_parameter_list.push(p);
                            });
                        } else {
                            // compare the parameter_list against our master parameters list
                            // if the master list contains a param not in this panel,
                            // remove it from the master list
                            var indices_to_exclude = [];
                            for (var i = 0; i < master_parameter_list.length; i++) {
                                if (parameter_list.indexOf(master_parameter_list[i]) == -1) {
                                    indices_to_exclude.push(i);
                                }
                            }
                        }
                        // either way we had a match so count it
                        panel_match_count++;
                    }
                });

                $scope.model.parameters = [];
                master_parameter_list.forEach(function (p) {
                    $scope.model.parameters.push(
                        {
                            parameter: p,
                            selected: true
                        }
                    );
                });
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

            $scope.updateSamples = function () {
                // Check the various categories and collect the checks! Ka-ching!

                var subject_list = [];
                $scope.model.subjects.forEach(function(subject) {
                    if (subject.selected) {
                        subject_list.push(subject.id);
                    }
                });

                var visit_list = [];
                $scope.model.visits.forEach(function(visit) {
                    if (visit.selected) {
                        visit_list.push(visit.id);
                    }
                });

                var stimulation_list = [];
                $scope.model.stimulations.forEach(function(stimulation) {
                    if (stimulation.selected) {
                        stimulation_list.push(stimulation.id);
                    }
                });

                var cytometer_list = [];
                $scope.model.cytometers.forEach(function(cytometer) {
                    if (cytometer.selected) {
                        cytometer_list.push(cytometer.id);
                    }
                });

                var pretreatment_list = [];
                $scope.model.pretreatments.forEach(function(pretreatment) {
                    if (pretreatment.selected) {
                        pretreatment_list.push(pretreatment.name);
                    }
                });

                // Now iterate over the samples to marking as ignore those not matching
                // the filters...but, there must be at least one filter item in
                // a category, else we won't filter
                $scope.model.samples.forEach(function (sample) {
                    var ignore = false;
                    if (subject_list.length > 0) {
                        if (subject_list.indexOf(sample.subject) == -1) {
                            ignore = true;
                        }
                    }
                    if (visit_list.length > 0) {
                        if (visit_list.indexOf(sample.visit) == -1) {
                            ignore = true;
                        }
                    }
                    if (stimulation_list.length > 0) {
                        if (stimulation_list.indexOf(sample.stimulation) == -1) {
                            ignore = true;
                        }
                    }
                    if (cytometer_list.length > 0) {
                        if (cytometer_list.indexOf(sample.cytometer) == -1) {
                            ignore = true;
                        }
                    }
                    if (pretreatment_list.length > 0) {
                        if (pretreatment_list.indexOf(sample.pretreatment) == -1) {
                            ignore = true;
                        }
                    }

                    sample.ignore = ignore;

                });
            };


        }
    ]
);