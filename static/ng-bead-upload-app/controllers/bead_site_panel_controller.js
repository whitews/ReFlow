/**
 * Created by swhite on 4/7/14.
 */
app.controller(
    'SitePanelController',
    [
        '$scope',
        'Fluorochrome',
        'SitePanel',
        function ($scope, Fluorochrome, SitePanel) {
            $scope.model.site_panel_url = '/static/ng-bead-upload-app/partials/create_bead_site_panel.html';
            $scope.model.fluorochromes = Fluorochrome.query();
            $scope.model.site_panel_errors = [];
            $scope.model.site_panel_valid = false;

            $scope.validatePanel = function() {
                // start with true and set to false on any error
                var valid = true;

                $scope.model.errors = [];

                if (!$scope.model.current_project_panel) {
                    $scope.model.errors.push('Please choose a panel template');
                    valid = false;
                    $scope.model.site_panel_valid = valid;
                    return valid;
                }

                var staining = $scope.model.current_project_panel.staining;
                if (staining != 'CB') {
                    $scope.model.errors.push('You must choose a compensation bead template');
                    valid = false;
                    $scope.model.site_panel_valid = valid;
                    return valid;
                }

                /*
                Validate the panel:
                    - Function and value type are required
                    - No fluorochromes in a scatter parameter
                    - Bead channels must specify a fluorochrome
                    - No duplicate fluorochrome + value type combinations
                    - No duplicate forward scatter + value type combinations
                    - No duplicate side scatter + value type combinations
                Validations against the parent panel template:
                    - Ensure all panel template parameters are present
                */
                var fluoro_duplicates = [];

                // reset all project param matches
                $scope.model.current_project_panel.parameters.forEach(function (p) {
                    p.match = false;
                });

                $scope.model.site_panel_sample.channels.forEach(function (channel) {
                    channel.errors = [];
                    // check for function
                    if (!channel.function) {
                        channel.errors.push('Function is required');
                    }
                    // check for value type
                    if (!channel.value_type) {
                        channel.errors.push('Value type is required');
                    }

                    // Check for fluoro duplicates
                    if (channel.fluorochrome) {
                        if (fluoro_duplicates.indexOf(channel.fluorochrome.toString() + "_" + channel.value_type) >= 0) {
                            channel.errors.push('The same fluorochrome cannot be in multiple channels');
                        } else {
                            fluoro_duplicates.push(channel.fluorochrome.toString() + "_" + channel.value_type);
                        }
                    }

                    // ensure no fluoro in scatter channels
                    if (channel.function == 'FSC' || channel.function == 'SSC') {
                        if (channel.fluorochrome) {
                            channel.errors.push('Scatter channels cannot have a fluorochrome');
                        }
                    }

                    // Time channels cannot have a fluoro or Ab, must have value type 'T'
                    if (channel.function == 'TIM') {
                        if (channel.fluorochrome) {
                            channel.errors.push('Time channel cannot specify a fluorochrome');
                        }
                        if (channel.value_type != 'T') {
                            channel.errors.push('Time channel must have time value type')
                        }
                    }

                    // Check if we match a template parameter
                    // starting with the required function / value type combo
                    for (var i = 0; i < $scope.model.current_project_panel.parameters.length; i++) {
                        // param var is just for better readability
                        var param = $scope.model.current_project_panel.parameters[i];

                        // first, check function
                        if (param.parameter_type != channel.function) {
                            // no match
                            continue;
                        }

                        // then value type
                        if (param.parameter_value_type != channel.value_type) {
                            // no match
                            continue;
                        }

                        // if template has fluoro, check it
                        if (param.fluorochrome) {
                            if (param.fluorochrome != channel.fluorochrome) {
                                // no match
                                continue;
                            }
                        }

                        // if we get here everything in the template matched
                        param.match = true;
                    }

                    if (channel.errors.length > 0 ) {
                        valid = false;
                    }
                });

                $scope.model.current_project_panel.parameters.forEach(function (p) {
                    if (!p.match) {
                        valid = false;
                    }
                });
                $scope.model.site_panel_valid = valid;
                return valid;
            };

            $scope.savePanel = function () {
                var is_valid = $scope.validatePanel();

                if (!is_valid) {
                    return;
                }

                var params = [];
                $scope.model.site_panel_sample.channels.forEach(function (c) {
                    params.push({
                        fcs_number: c.channel,
                        fcs_text: c.pnn,
                        fcs_opt_text: c.pns,
                        parameter_type: c.function,
                        parameter_value_type: c.value_type,
                        markers: [],
                        fluorochrome: c.fluorochrome || null
                    })
                });
                var data = {
                    site: $scope.model.current_site.id,
                    project_panel: $scope.model.current_project_panel.id,
                    parameters: params,
                    site_panel_comments: ""
                };
                var site_panel = SitePanel.save(data);
                site_panel.$promise.then(function (o) {
                    $scope.model.close_modal = true;
                    // broadcast to update site panels and set
                    // current site panel to this one, we broadcast to root
                    // b/c there's no relationship between this and site panel
                    // query controller
                    $scope.$root.$broadcast('updateSitePanels', o.id);
                }, function(error) {
                    console.log(error);
                });
            };
        }
    ]
);


app.controller(
    'ParameterController',
    [
        '$scope',
        'ParameterFunction',
        'ParameterValueType',
        function ($scope, ParameterFunction, ParameterValueType) {
            $scope.model.parameter_functions = [
                ["FSC", "Forward Scatter"],
                ["SSC", "Side Scatter"],
                ["BEA", "Bead"],
                ["TIM", "Time"]
            ];

            $scope.model.parameter_value_types = ParameterValueType.query();
        }
    ]
);


app.controller(
    'SitePanelCreationProjectPanelController',
    ['$scope', 'ProjectPanel', function ($scope, ProjectPanel) {
        $scope.$on('initSitePanel', function (o, f) {
            $scope.model.close_modal = false;
            $scope.model.current_project_panel = null;
            $scope.model.project_panels = ProjectPanel.query(
                {
                    project: $scope.model.current_project.id,
                    staining: 'CB'
                }
            );
            $scope.model.site_panel_sample = f;

            $scope.model.site_panel_sample.channels.forEach(function (c) {
                c.function = null;
                c.errors = [];

                // Check the PnN field for 'FSC' or 'SSC'
                if (c.pnn.substr(0, 3) == 'FSC') {
                    c.function = 'FSC';
                    c.fluoro_disabled = true;
                } else if (c.pnn.substr(0, 3) == 'SSC') {
                    c.function = 'SSC';
                    c.fluoro_disabled = true;
                } else if (c.pnn.substr(0, 4) == 'Time') {
                    c.function = 'TIM';
                    c.fluoro_disabled = true;
                }

                // Check the PnN field for value type using the last 2 letters
                if (c.pnn.substr(-2) == '-A') {
                    c.value_type = 'A';
                } else if (c.pnn.substr(-2) == '-H') {
                    c.value_type = 'H';
                } else if (c.pnn.substr(-2) == '-W') {
                    c.value_type = 'W';
                } else if (c.pnn.substr(-2) == '-T' || c.pnn.substr(0, 4) == 'Time') {
                    c.value_type = 'T';
                }

                if (!c.function) {
                    var pattern = /\w+/g;
                    var words = (c.pnn + ' ' + c.pns).match(pattern);

                    // for the fluorochromes, matching is a bit tricky b/c of tandem dyes
                    // we'll need to check against the longest match in the entire
                    // fcs_text first and then the words
                    var fl_match = '';
                    $scope.model.fluorochromes.forEach(function(f) {
                        // strip out non-alphanumeric chars
                        fluoro_str = f.fluorochrome_abbreviation.replace(/[^A-Z,a-z,0-9]/g,"");
                        pnn_str = c.pnn.replace(/[^A-Z,a-z,0-9]/g,"");
                        pns_str = c.pns.replace(/[^A-Z,a-z,0-9]/g,"");

                        if (pnn_str.indexOf(fluoro_str) >= 0) {
                            if (fluoro_str.length > fl_match.length) {
                                fl_match = fluoro_str;
                                c.fluorochrome = f.id;
                            }
                        } else if (pns_str.indexOf(fluoro_str) >= 0) {
                            if (fluoro_str.length > fl_match.length) {
                                fl_match = fluoro_str;
                                c.fluorochrome = f.id;
                            }
                        }
                    });

                    if (c.fluorochrome != null) {
                        c.function = 'BEA';
                    }

                }
            });
        });
    }
]);