/**
 * Created by swhite on 2/25/14.
 */

app.controller(
    'ProcessRequestController',
    [
        '$scope',
        '$controller',
        'ProcessRequest',
        function ($scope, $controller, ProcessRequest) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            function get_list() {
                return ProcessRequest.query(
                    {
                        'project': $scope.current_project.id
                    }
                );
            }

            if ($scope.current_project != undefined) {
                $scope.process_requests = get_list();
            } else {
                $scope.$on('currentProjectSet', function () {
                    $scope.process_requests = get_list();
                });
            }

            $scope.$on('updateProcessRequests', function () {
                $scope.process_requests = get_list();
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
        'ProcessRequest',
        'ProcessRequestInput',
        'ProcessRequestOutput',
        function ($scope, $controller, $stateParams, ProcessRequest, ProcessRequestInput, ProcessRequestOutput) {
            // Inherits ProcessRequestController $scope
            $controller('ProcessRequestController', {$scope: $scope});

            $scope.process_request = ProcessRequest.get(
                { id: $stateParams.requestId }
            );
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
        '$controller',
        '$modal',
        'Project',
        'Site',
        'PanelTemplate',
        'SitePanel',
        'Sample',
        'SampleCollection',
        'SampleCollectionMember',
        'Subject',
        'VisitType',
        'Stimulation',
        'Cytometer',
        'Pretreatment',
        'SubprocessImplementation',
        'SubprocessInput',
        'ProcessRequest',
        'ProcessRequestInput',
        function (
                $scope,
                $controller,
                $modal,
                Project,
                Site,
                PanelTemplate,
                SitePanel,
                Sample,
                SampleCollection,
                SampleCollectionMember,
                Subject,
                VisitType,
                Stimulation,
                Cytometer,
                Pretreatment,
                SubprocessImplementation,
                SubprocessInput,
                ProcessRequest,
                ProcessRequestInput) {

            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.model = {};

            // Populate our sample filters
            $scope.model.panel_templates = PanelTemplate.query({project: $scope.current_project.id});
            $scope.model.site_panels = []; // depends on chosen template
            $scope.model.sites = Site.query({project: $scope.current_project.id});
            $scope.model.subjects = Subject.query({project: $scope.current_project.id});
            $scope.model.visits = VisitType.query({project: $scope.current_project.id});
            $scope.model.stimulations = Stimulation.query({project: $scope.current_project.id});
            $scope.model.cytometers = []; // depends on chosen sites
            $scope.model.pretreatments = Pretreatment.query();

            $scope.model.current_panel_template = null;

            $scope.panelTemplateChanged = function () {
                $scope.model.samples = Sample.query({panel: $scope.model.current_panel_template.id});

                $scope.model.samples.$promise.then(function (data) {
                    data.forEach(function (sample) {
                        sample.ignore = false;
                        sample.selected = true;
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
                $scope.model.cytometers = Cytometer.query({site: site_list});
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
                SubprocessImplementation.query(
                    {
                        category_name: category_name,
                        name: implementation_name
                    },
                    function (data) {  // success
                        if (data.length > 0) {
                            $scope.model.filtering = data[0];
                        }
                    }
                );

                $scope.model.parameter_inputs = SubprocessInput.query(
                    {
                        category_name: category_name,
                        implementation_name: implementation_name,
                        name: subproc_name
                    }
                ); // there should only be one 'parameter' subproc input
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

                $scope.model.site_panels = SitePanel.query({'id': site_panel_list});

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
                            $scope.model.parameters.push(
                                {
                                    parameter: master_parameter_list[i],
                                    selected: true
                                }
                            );
                        }
                    }
                });
            }

            function initializeTransformation () {
                // there's only one transform implementation now (logicle)
                // so we'll go ahead to retrieve the inputs for that
                // implementation
                var category_name = 'transformation';
                var implementation_name = 'asinh';
                SubprocessImplementation.query(
                    {
                        category_name: category_name,
                        name: implementation_name
                    },
                    function (data) {  // success
                        if (data.length > 0) {
                            $scope.model.transformation = data[0];
                        }
                    }
                );

                $scope.model.transform_inputs = SubprocessInput.query(
                    {
                        category_name: category_name,
                        implementation_name: implementation_name
                    },
                    function (data) {  // success
                        data.forEach(function (input) {
                            input.value = input.default;
                        });
                    }
                );
            }

            function initializeClustering () {
                // there's only one clustering implementation now (hdp)
                // so we'll go ahead to retrieve the inputs for that
                // implementation
                var category_name = 'clustering';
                var implementation_name = 'hdp';
                SubprocessImplementation.query(
                    {
                        category_name: category_name,
                        name: implementation_name
                    },
                    function (data) {  // success
                        if (data.length > 0) {
                            $scope.model.clustering = data[0];
                        }
                    }
                );

                $scope.model.clustering_inputs = SubprocessInput.query(
                    {
                        category_name: category_name,
                        implementation_name: implementation_name
                    },
                    function (data) {  // success
                        data.forEach(function (input) {
                            input.value = input.default;
                        });
                    }
                );
            }

            function initializeStep () {
                switch ($scope.current_step.name) {
                    case "filter_samples":
                        initializeSamples();
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

            $scope.submit_request = function () {
                // first, we'll create the sample collection using the project ID
                var collection = SampleCollection.save(
                    {
                        project: $scope.current_project.id
                    }
                );

                // then, create the sample collection members using the
                // sample collection ID
                var pr = collection.$promise
                    .then(function (c) {
                        var members = [];
                        $scope.model.samples.forEach(function (sample) {
                            if (sample.selected && !sample.ignore) {
                                members.push(
                                    new SampleCollectionMember(
                                        {
                                            sample_collection: c.id,
                                            sample: sample.id
                                        }
                                    )
                                )
                            }
                        });
                        SampleCollectionMember.save(members);
                    })
                    .then(function () {  // Create the PR before the inputs
                        var pr = new ProcessRequest(
                            {
                                project: $scope.current_project.id,
                                sample_collection: collection.id,
                                description: $scope.model.request_description
                            }
                        );
                        return ProcessRequest.save(pr).$promise;
                    });

                pr.then(function (pr) {  // create all the PR inputs
                    var pr_inputs = [];

                    // first retrieve the chosen parameters
                    var param_subproc = $scope.model.parameter_inputs[0];
                    $scope.model.parameters.forEach(function (param) {
                        if (param.selected) {
                            pr_inputs.push(
                                new ProcessRequestInput(
                                    {
                                        process_request: pr.id,
                                        subprocess_input: param_subproc.id,
                                        value: param.parameter
                                    }
                                )
                            )
                        }
                    });

                    // next get the transformation inputs
                    $scope.model.transform_inputs.forEach(function (input) {
                        pr_inputs.push(
                            new ProcessRequestInput(
                                {
                                    process_request: pr.id,
                                    subprocess_input: input.id,
                                    value: input.value
                                }
                            )
                        )
                    });

                    // and the clustering inputs
                    $scope.model.clustering_inputs.forEach(function (input) {
                        pr_inputs.push(
                            new ProcessRequestInput(
                                {
                                    process_request: pr.id,
                                    subprocess_input: input.id,
                                    value: input.value
                                }
                            )
                        )
                    });

                    // and we're ready to save them all in bulk
                    ProcessRequestInput.save(
                        pr_inputs,
                        function (data) {  // success
                            $scope.nextStep();
                            $scope.model.submitted_pr = pr;
                            $scope.model.submitted_pr_inputs = data;
                    })
                });
            }
        }
    ]
);