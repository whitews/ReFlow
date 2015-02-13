app.controller(
    'SitePanelController',
    ['$scope', '$controller', 'ModelService', function ($scope, $controller, ModelService) {
        // Inherits ProjectDetailController $scope
        $controller('ProjectDetailController', {$scope: $scope});

        function get_list() {
            var response = ModelService.getSitePanels(
                {
                    'project': $scope.current_project.id
                }
            );

            $scope.expand_params = [];
            response.$promise.then(function (site_panels) {
                site_panels.forEach(function () {
                    $scope.expand_params.push(false);
                })
            });
            return response;
        }

        if ($scope.current_project != undefined) {
            $scope.site_panels = get_list();
        }

        $scope.$on('current_project:updated', function () {
            $scope.site_panels = get_list();
        });

        $scope.$on('site_panels:updated', function () {
            $scope.site_panels = get_list();
        });

        $scope.toggle_params = function (i) {
            $scope.expand_params[i] = $scope.expand_params[i] != true;
        };

        $scope.expand_all_panels = function () {
            for (var i = 0; i < $scope.site_panels.length; i++) {
                $scope.expand_params[i] = true;
            }
        };

        $scope.collapse_all_panels = function () {
            for (var i = 0; i < $scope.site_panels.length; i++) {
                $scope.expand_params[i] = false;
            }
        };
    }
]);

app.controller(
    'SitePanelCreateController',
    ['$scope', '$q', 'ModelService', function ($scope, $q, ModelService) {

        $scope.site_panel_model = {};
        $scope.close_modal = false;
        $scope.site_panel_model.current_site = ModelService.getCurrentSite();
        $scope.site_panel_model.site_panel_sample = ModelService.getCurrentSample();
        $scope.site_panel_model.current_panel_template = ModelService.getCurrentPanelTemplate();

        $scope.site_panel_model.markers = ModelService.getMarkers();
        $scope.site_panel_model.fluorochromes = ModelService.getFluorochromes();

        // everything but bead functions
        // TODO: convert to ModelService call
        $scope.site_panel_model.parameter_functions = [
            ["FSC", "Forward Scatter"],
            ["SSC", "Side Scatter"],
            ["FLR", "Fluorescence"],
            ["TIM", "Time"],
            ["NUL", "Null"]
        ];

        $scope.site_panel_model.parameter_value_types = ModelService.getParameterValueTypes();

        $scope.site_panel_model.site_panel_errors = [];
        $scope.site_panel_model.site_panel_valid = false;

        // wait for all promises to return then initialize the site panel
        $q.all([
            $scope.site_panel_model.markers.$promise,
            $scope.site_panel_model.fluorochromes.$promise,
            $scope.site_panel_model.parameter_value_types.$promise
        ]).then(function(result) {
            initSitePanel();
        });

        $scope.validatePanel = function() {
            // start with true and set to false on any error
            var valid = true;

            $scope.site_panel_model.errors = [];

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

            var fluoro_duplicates = [];

            // reset all project param matches
            $scope.site_panel_model.current_panel_template.parameters.forEach(function (p) {
                p.match = false;
            });

            $scope.site_panel_model.site_panel_sample.channels.forEach(function (channel) {
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

                // fluoro channels must have a fluorochrome
                if (channel.function == 'FLR') {
                    if (!channel.fluorochrome) {
                        channel.errors.push('Fluorescence channels must specify a fluorochrome');
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
                for (var i = 0; i < $scope.site_panel_model.current_panel_template.parameters.length; i++) {
                    // param var is just for better readability
                    var param = $scope.site_panel_model.current_panel_template.parameters[i];

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
                            if (channel.markers.indexOf(param.markers[j].marker_id) == -1) {
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

            $scope.site_panel_model.current_panel_template.parameters.forEach(function (p) {
                if (!p.match) {
                    valid = false;
                }
            });
            $scope.site_panel_model.site_panel_valid = valid;
            return valid;
        };

        function initSitePanel() {
            $scope.site_panel_model.site_panel_sample.channels.forEach(function (c) {
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
                } else {
                    c.function = 'FLR';
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
                if (c.function == 'FLR') {
                    var pattern = /\w+/g;
                    var words = (c.pnn + ' ' + c.pns).match(pattern);

                    // find matching markers
                    $scope.site_panel_model.markers.forEach(function(m) {
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
                    $scope.site_panel_model.fluorochromes.forEach(function(f) {
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
                }
            });
            $scope.validatePanel();
        }

        $scope.savePanel = function () {
            var is_valid = $scope.validatePanel();

            if (!is_valid) {
                return;
            }

            var params = [];
            $scope.site_panel_model.site_panel_sample.channels.forEach(function (c) {
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
                site: $scope.site_panel_model.current_site.id,
                panel_template: $scope.site_panel_model.current_panel_template.id,
                parameters: params,
                site_panel_comments: ""
            };
            var site_panel = ModelService.createSitePanel(data);
            site_panel.$promise.then(function () {
                // notify to update site panels
                ModelService.sitePanelsUpdated();
                // close modal
                $scope.ok();
            }, function(error) {
                console.log(error);
            });
        };
    }
]);