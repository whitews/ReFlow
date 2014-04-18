/**
 * Created by swhite on 4/7/14.
 */
app.controller(
    'SitePanelController',
    [
        '$scope',
        'Marker',
        'Fluorochrome',
        'SitePanel',
        function ($scope, Marker, Fluorochrome, SitePanel) {
            $scope.model.site_panel_url = '/static/ng-fcs-upload-app/partials/create_site_panel.html';
            $scope.model.markers = Marker.query();
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

                /*
                Validate the panel:
                    - Function and value type are required
                    - No fluorochromes in a scatter parameter
                    - No markers in a scatter parameter
                    - Fluoroscent parameter must specify a fluorochrome
                    - No duplicate fluorochrome + value type combinations
                    - No duplicate forward scatter + value type combinations
                    - No duplicate side scatter + value type combinations
                Validations against the parent panel template:
                    - Ensure all panel template parameters are present
                */
                var staining = $scope.model.current_project_panel.staining;
                var can_have_uns = null;
                var can_have_iso = null;
                var fluoro_duplicates = [];
                switch (staining) {
                    case 'IS':
                        can_have_uns = false;
                        can_have_iso = true;
                        break;
                    default :  // includes FS, FM, & US
                        can_have_uns = true;
                        can_have_iso = false;
                }

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

                    // ensure no fluoro or markers in scatter channels
                    if (channel.function == 'FSC' || channel.function == 'SSC') {
                        if (channel.fluorochrome) {
                            channel.errors.push('Scatter channels cannot have a fluorochrome');
                        }
                        if (channel.markers.length > 0) {
                            channel.errors.push('Scatter channels cannot have markers');
                        }
                    }

                    if (!can_have_uns && channel.function == 'UNS') {
                        channel.errors.push(staining + ' panels cannot have unstained channels');
                    }
                    if (!can_have_iso && channel.function == 'ISO') {
                        channel.errors.push('Only Iso panels can include iso channels');
                    }

                    // exclusion channels must include a fluoro
                    if (channel.function == 'EXC' && !channel.fluorochrome) {
                        channel.errors.push('Exclusion channels must specify a fluorochrome');
                    }

                    // fluoro conjugate channels must have both fluoro and Ab
                    if (channel.function == 'FCM') {
                        if (!channel.fluorochrome) {
                            channel.errors.push('Conjugated channels must specify a fluorochrome');
                        }
                        if (channel.markers.length < 1) {
                            channel.errors.push('Conjugated channels must specify at least one marker');
                        }
                    }

                    // unstained channels cannot have a fluoro but must have an Ab
                    if (channel.function == 'UNS') {
                        if (channel.fluorochrome) {
                            channel.errors.push('Unstained channels cannot specify a fluorochrome');
                        }
                        if (channel.markers.length < 1) {
                            channel.errors.push('Unstained channels must specify at least one marker');
                        }
                    }

                    // Iso channels must have a fluoro, cannot have an Ab
                    if (channel.function == 'ISO') {
                        if (!channel.fluorochrome) {
                            channel.errors.push('Iso channels must specify a fluorochrome');
                        }
                        if (channel.markers.length > 0) {
                            channel.errors.push('Iso channels cannot have markers');
                        }
                    }

                    // Time channels cannot have a fluoro or Ab, must have value type 'T'
                    if (channel.function == 'TIM') {
                        if (channel.fluorochrome) {
                            channel.errors.push('Time channel cannot specify a fluorochrome');
                        }
                        if (channel.markers.length > 0) {
                            channel.errors.push('Time channel cannot have markers');
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

                        // if template has markers, check them all
                        if (param.markers.length > 0) {
                            var marker_match = true;
                            for (var j = 0; j < param.markers.length; j++) {
                                if (channel.markers.indexOf(param.markers[j].marker_id.toString()) == -1) {
                                    // no match
                                    marker_match = false;
                                    break;
                                }
                            }
                            if (!marker_match) {
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
                        markers: c.markers,
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
            $scope.model.parameter_functions = ParameterFunction.query();
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
                    project: $scope.model.current_project.id
                }
            );
            $scope.model.site_panel_sample = f;

            $scope.model.site_panel_sample.channels.forEach(function (c) {
                c.function = null;
                c.errors = [];

                // Check the PnN field for 'FSC' or 'SSC'
                if (c.pnn.substr(0, 3) == 'FSC') {
                    c.function = 'FSC';
                    c.marker_disabled = true;
                    c.fluoro_disabled = true;
                } else if (c.pnn.substr(0, 3) == 'SSC') {
                    c.function = 'SSC';
                    c.marker_disabled = true;
                    c.fluoro_disabled = true;
                } else if (c.pnn.substr(0, 4) == 'Time') {
                    c.function = 'TIM';
                    c.marker_disabled = true;
                    c.fluoro_disabled = true;
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

                c.markers = [];
                if (!c.function) {
                    var pattern = /\w+/g;
                    var words = (c.pnn + ' ' + c.pns).match(pattern);

                    // find matching markers
                    $scope.model.markers.forEach(function(m) {
                        words.forEach(function(w) {
                            if (m.marker_abbreviation.replace(/[^A-Z,a-z,0-9]/g,"") === w.replace(/[^A-Z,a-z,0-9]/g,"")) {
                                c.markers.push(m.id.toString());
                            }
                        });
                    });

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

                    if (c.markers.length > 0 && c.fluorochrome != null) {
                        c.function = 'FCM';
                    }

                }
            });
        });
    }
]);