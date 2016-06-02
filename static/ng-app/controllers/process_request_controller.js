app.controller(
    'ProcessRequestController',
    [
        '$scope',
        '$controller',
        'ModelService',
        function ($scope, $controller, ModelService) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            if ($scope.current_project) {
                $scope.process_requests = ModelService.getProcessRequests(
                    {
                        'project': $scope.current_project.id
                    }
                );
            }

            $scope.$on('current_project:updated', function () {
                $scope.process_requests = ModelService.getProcessRequests(
                    {
                        'project': $scope.current_project.id
                    }
                );
            });

            $scope.$on('process_requests:updated', function () {
                $scope.process_requests = ModelService.getProcessRequests(
                    {
                        'project': $scope.current_project.id
                    }
                );
            });
        }
    ]
);

app.controller(
    'ProcessRequestDetailController',
    [
        '$scope',
        '$controller',
        '$stateParams',
        '$interval',
        'ModelService',
        function ($scope, $controller, $stateParams, $interval, ModelService) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            var progress_interval;

            $scope.process_request = ModelService.getProcessRequest(
                $stateParams.requestId
            );

            $scope.process_request.$promise.then(function (pr) {
                // get sample collection for this PR
                ModelService.getSampleCollection(
                    $scope.process_request.sample_collection
                ).$promise.then(function (data) {
                    $scope.sample_collection = data;
                });

                // get child 2nd stage PRs related to this PR
                ModelService.getProcessRequests(
                    {
                        parent_stage: pr.id
                    }
                ).$promise.then(function (data) {
                    $scope.children = data;
                });

                // finally, for 'Working' PRs, set up interval to track progress
                if (pr.status === 'Working' || pr.status === 'Pending') {
                    // update progress every 15 seconds
                    progress_interval = $interval(update_progress, 15000);
                }
            });

            $scope.$on("$destroy", function() {
                if (progress_interval) {
                    kill_progress_interval();
                }
            });

            function update_progress() {
                // call to model service here
                var progress_update = ModelService.getProcessRequestProgress(
                    $scope.process_request.id
                );
                progress_update.$promise.then(function(pr_progress) {
                    $scope.process_request.status = pr_progress.status;
                    $scope.process_request.status_message = pr_progress.status_message;
                    $scope.process_request.percent_complete = pr_progress.percent_complete;
                    if (pr_progress.status === 'Complete' || pr_progress.status === 'Error') {
                        kill_progress_interval();
                    }
                });
            }

            function kill_progress_interval() {
                $interval.cancel(progress_interval);
            }
        }
    ]
);

var process_steps = [
    {
        "name": "filter_samples",
        "title": "Choose Samples",
        "url": "/static/ng-app/partials/pr/choose_samples.html"
    },
    {
        "name": "choose_compensations",
        "title": "Choose Compensations",
        "url": "/static/ng-app/partials/pr/choose_compensations.html"
    },
    {
        "name": "filter_parameters",
        "title": "Choose Parameters",
        "url": "/static/ng-app/partials/pr/choose_parameters.html"
    },
    {
        "name": "transformation_options",
        "title": "Transformation Options",
        "url": "/static/ng-app/partials/pr/transformation_options.html"
    },
    {
        "name": "clustering_options",
        "title": "Clustering Options",
        "url": "/static/ng-app/partials/pr/clustering_options.html"
    },
    {
        "name": "process_request_options",
        "title": "Process Request Options",
        "url": "/static/ng-app/partials/pr/request_options.html"
    },
    {
        "name": "success",
        "title": "Process Request Submitted",
        "url": "/static/ng-app/partials/pr/success.html"
    }
];

app.controller(
    'ProcessRequestFormController',
    [
        '$scope',
        '$q',
        '$controller',
        '$modal',
        'ModelService',
        function (
                $scope,
                $q,
                $controller,
                $modal,
                ModelService) {

            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.model = {
                'subsample_count': 10000  // default sub-sample count is 10k
            };

            function init_filters() {
                // Populate our sample filters
                $scope.model.panel_templates = ModelService.getPanelTemplates(
                    {project: $scope.current_project.id}
                );
                $scope.model.site_panels = []; // depends on chosen template
                $scope.model.sites = ModelService.getSites($scope.current_project.id);
                $scope.model.subjects = ModelService.getSubjects($scope.current_project.id);
                $scope.model.visits = ModelService.getVisitTypes($scope.current_project.id);
                $scope.model.stimulations = ModelService.getStimulations($scope.current_project.id);
                $scope.model.pretreatments = ModelService.getPretreatments();
                $scope.model.chosen_samples = [];
                $scope.model.comp_object_lut = {};

                $scope.model.current_panel_template = null;
            }

            if ($scope.current_project) {
                init_filters();
            }

            $scope.$on('current_project:updated', function () {
                init_filters();
            });

            $scope.panelTemplateChanged = function () {
                $scope.model.samples = ModelService.getSamples(
                    {
                        panel: $scope.model.current_panel_template.id
                    }
                );

                $scope.model.samples.$promise.then(function (data) {
                    data.forEach(function (sample) {
                        sample.ignore = false;
                        sample.selected = true;
                        sample.comp_candidates = ModelService.getCompensations(
                            {
                                'site_panel': sample.site_panel,
                                'acquisition_date': sample.acquisition_date
                            }
                        );
                        sample.chosen_comp_matrix = null;
                        sample.comp_candidates.$promise.then(function(comps) {
                            /*
                             * TODO: improve auto-choice in the future to
                             * choose any matrix with the same name as the
                             * sample's original file name
                             */
                            if (comps.length > 0) {
                                sample.chosen_comp_matrix = comps[0].id;
                            }

                            comps.forEach(function (c) {
                                if (!$scope.model.comp_object_lut.hasOwnProperty(c.id)) {
                                    $scope.model.comp_object_lut[c.id] = ModelService.getCompensationCSV(c.id);
                                }
                            });
                        });
                    });

                    $scope.updateSamples();
                })
            };

            $scope.siteSelectionChanged = function () {
                var site_list = [];
                $scope.model.sites.forEach(function(site) {
                    if (site.selected) {
                        site_list.push(site.id);
                    }
                });
                $scope.updateSamples();
            };

            $scope.current_step_index = 0;
            $scope.step_count = process_steps.length;
            $scope.current_step = process_steps[$scope.current_step_index];
            initializeStep();

            function initializeSamples () {
                var category_name = 'filtering';
                var implementation_name = 'parameters';
                var subproc_name = 'parameter';
                ModelService.getSubprocessImplementations(
                    {
                        category_name: category_name,
                        name: implementation_name
                    }
                ).$promise.then(function (data) {
                    if (data.length > 0) {
                        $scope.model.filtering = data[0];
                    }
                });

                $scope.model.parameter_inputs = ModelService.getSubprocessInputs(
                    {
                        category_name: category_name,
                        implementation_name: implementation_name,
                        name: subproc_name
                    }
                ); // there should only be one 'parameter' subproc input
            }

            function initializeCompensations () {
                // Iterate samples that are both selected and not ignored
                // to collect compensation candidates
                $scope.model.chosen_samples = [];
                $scope.model.samples.forEach(function (sample) {
                    if (sample.selected && !sample.ignore) {
                        $scope.model.chosen_samples.push(sample)
                    }
                });
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
                var indices_to_exclude = [];

                $scope.model.site_panels = ModelService.getSitePanels(
                    {
                        'id': site_panel_list
                    }
                );

                $scope.model.site_panels.$promise.then(function(data) {
                    data.forEach (function (site_panel) {
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
                                    parameter.parameter_value_type;
                                if (marker_string) {
                                    param_string = param_string + "_" + marker_string;
                                }
                                if (parameter.fluorochrome) {
                                    param_string = param_string + "_" + parameter.fluorochrome.fluorochrome_abbreviation;
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
                    for (var i = 0; i < master_parameter_list.length; i++) {
                        if (indices_to_exclude.indexOf(i) == -1) {
                            // by default, don't show NULL or TIME params
                            if (["NUL", "TIM"].indexOf(master_parameter_list[i].substr(0, 3)) != -1) {
                                continue;
                            } else {
                                $scope.model.parameters.push(
                                    {
                                        parameter: master_parameter_list[i],
                                        selected: false
                                    }
                                );
                            }
                        }
                    }
                });
            }

            function initializeTransformation () {
                // there's only one transform implementation now (asinh)
                // so we'll go ahead to retrieve the inputs for that
                // implementation
                var category_name = 'transformation';
                var implementation_name = 'asinh';

                ModelService.getSubprocessImplementations(
                    {
                        category_name: category_name,
                        name: implementation_name
                    }
                ).$promise.then(function (data) {
                    if (data.length > 0) {
                        $scope.model.transformation = data[0];
                    }
                });

                $scope.model.transform_inputs = ModelService.getSubprocessInputs(
                    {
                        category_name: category_name,
                        implementation_name: implementation_name
                    }
                );
                $scope.model.transform_inputs.$promise.then(function () {
                    $scope.model.transform_inputs.forEach(function (input) {
                        input.value = input.default;
                    });
                });
            }

            function initializeClustering () {
                // there's only one clustering implementation now (hdp)
                // so we'll go ahead to retrieve the inputs for that
                // implementation
                var category_name = 'clustering';
                var implementation_name = 'hdp';

                ModelService.getSubprocessImplementations(
                    {
                        category_name: category_name,
                        name: implementation_name
                    }
                ).$promise.then(function (data) {
                    if (data.length > 0) {
                        $scope.model.clustering = data[0];
                    }
                });

                $scope.model.clustering_inputs = ModelService.getSubprocessInputs(
                    {
                        category_name: category_name,
                        implementation_name: implementation_name
                    }
                );
                $scope.model.clustering_inputs.$promise.then(function () {
                    $scope.model.clustering_inputs.forEach(function (input) {
                        input.value = input.default;
                    });
                });
            }

            function initializeStep () {
                switch ($scope.current_step.name) {
                    case "filter_samples":
                        initializeSamples();
                        break;
                    case "choose_compensations":
                        initializeCompensations();
                        break;
                    case "filter_parameters":
                        initializeParameters();
                        break;
                    case "transformation_options":
                        initializeTransformation();
                        break;
                    case "clustering_options":
                        initializeClustering();
                        break;
                    case "process_request_options":
                        break;
                    case "success":
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
            $scope.firstStep = function () {
                $scope.current_step_index = 0;
                $scope.current_step = process_steps[$scope.current_step_index];
                initializeStep();
            };

            $scope.toggleAllSamples = function () {
                $scope.model.samples.forEach(function(sample) {
                    sample.selected = $scope.model.master_sample_checkbox;
                });
            };

            $scope.toggleAllParameters = function () {
                $scope.model.parameters.forEach(function(param) {
                    param.selected = $scope.model.master_parameter_checkbox;
                });
            };

            $scope.updateSamples = function () {
                // Check the various categories and collect the checks! Ka-ching!

                var site_list = [];
                $scope.model.sites.forEach(function(site) {
                    if (site.selected) {
                        site_list.push(site.id);
                    }
                });

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
                    if (site_list.length > 0) {
                        if (site_list.indexOf(sample.site) == -1) {
                            ignore = true;
                        }
                    }
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
                    if (pretreatment_list.length > 0) {
                        if (pretreatment_list.indexOf(sample.pretreatment) == -1) {
                            ignore = true;
                        }
                    }

                    sample.ignore = ignore;

                });
            };

            $scope.submit_request = function () {
                // first, we'll create the sample collection using the project ID
                var collection = ModelService.createSampleCollection(
                    {
                        project: $scope.current_project.id
                    }
                );

                // then, create the sample collection members & PR using the
                // sample collection ID
                collection.$promise.then(function () {
                    var member_objects = [];
                    $scope.model.samples.forEach(function (sample) {
                        if (sample.selected && !sample.ignore) {
                            member_objects.push(
                                {
                                    sample_collection: collection.id,
                                    sample: sample.id,
                                    compensation: $scope.model.comp_object_lut[sample.chosen_comp_matrix].matrix
                                }
                            );
                        }
                    });

                    var members = ModelService.createSampleCollectionMembers(
                        member_objects
                    );
                    var pr = ModelService.createProcessRequest(
                        {
                            project: $scope.current_project.id,
                            sample_collection: collection.id,
                            description: $scope.model.request_description,
                            subsample_count: $scope.model.subsample_count
                        }
                    );
                    $q.all([members.$promise, pr.$promise]).then(function () {
                        // finally, create all the PR inputs
                        var pr_input_objects = [];

                        // first retrieve the chosen parameters
                        var param_subproc = $scope.model.parameter_inputs[0];
                        $scope.model.parameters.forEach(function (param) {
                            if (param.selected) {
                                pr_input_objects.push(
                                    {
                                        process_request: pr.id,
                                        subprocess_input: param_subproc.id,
                                        value: param.parameter
                                    }
                                );
                            }
                        });

                        // next get the transformation inputs
                        $scope.model.transform_inputs.forEach(function (input) {
                            pr_input_objects.push(
                                {
                                    process_request: pr.id,
                                    subprocess_input: input.id,
                                    value: input.value
                                }
                            );
                        });

                        // and the clustering inputs
                        $scope.model.clustering_inputs.forEach(function (input) {
                            pr_input_objects.push(
                                {
                                    process_request: pr.id,
                                    subprocess_input: input.id,
                                    value: input.value
                                }
                            );
                        });

                        // and we're ready to save them all in bulk
                        var pr_inputs = ModelService.createProcessRequestInputs(
                            pr_input_objects
                        );
                        pr_inputs.$promise.then(function (data) {
                            $scope.nextStep();
                            $scope.model.submitted_pr = pr;
                            $scope.model.submitted_pr_inputs = data;
                        });
                    });

                });
            };
        }
    ]
);