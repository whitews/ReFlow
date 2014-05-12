app.controller(
    'MainController',
    [
        '$scope', '$window', '$routeParams', 'Project', 'ProjectPanel', 'Marker', 'Fluorochrome',
        function ($scope, $window, $routeParams, Project, ProjectPanel, Marker, Fluorochrome) {
            $scope.model = {};
            $scope.model.markers = Marker.query();
            $scope.model.fluorochromes = Fluorochrome.query();
            $scope.model.projects = Project.query();

            $scope.model.panel_template_types = [
                ["FS", "Full Stain"],
                ["US", "Unstained"],
                ["FM", "Fluorescence Minus One"],
                ["IS", "Isotype Control"],
                ["CB", "Compensation Bead"]
            ];

            $scope.model.parameter_errors = [];
            $scope.model.template_valid = false;

            if ($routeParams['template_id']) {
                var template_id = $routeParams['template_id'];
                $scope.model.template = ProjectPanel.get(
                    {id: template_id},
                    function () {
                        $scope.model.panel_name = $scope.model.template.panel_name;
                        $scope.model.current_staining = $scope.model.template.staining;
                        $scope.model.current_project = $scope.model.template.project;
                        $scope.model.channels = [];
                        $scope.model.template.parameters.forEach(function (p) {
                            var channel = {markers: []};
                            if (p.parameter_type) {
                                channel.function = p.parameter_type;
                            }
                            if (p.parameter_value_type) {
                                channel.value_type = p.parameter_value_type;
                            }
                            if (p.markers.length > 0) {
                                p.markers.forEach(function (m) {
                                    channel.markers.push(m.marker_id);
                                });
                            }
                            if (p.fluorochrome) {
                                channel.fluorochrome = p.fluorochrome;
                            }

                            $scope.model.channels.push(channel);
                        });
                        $scope.validatePanel();
                    }
                );
            } else {
                $scope.model.parent_template = null;
                $scope.model.channels = [{markers: []}];
            }

            $scope.updateParentTemplates = function() {
                // get all project panel templates
                var staining;
                if ($scope.model.current_staining) {
                    staining = [$scope.model.current_staining];
                    if (staining != 'FS') {
                        $scope.model.parent_template_required = true;
                    }
                } else {
                    staining = ['FS', 'US', 'FM', 'IS'];
                    $scope.model.parent_template_required = false;
                }
                $scope.model.panel_templates = ProjectPanel.query(
                    {
                        project: $scope.model.current_project,
                        staining: staining
                    }
                );
                $scope.validatePanel();
            };

            $scope.addChannel = function() {
                $scope.model.channels.push({markers:[]});
            };

            $scope.removeChannel = function(channel) {
                $scope.model.channels.splice($scope.model.channels.indexOf(channel), 1);
            };

            $scope.validatePanel = function() {
                // start with true and set to false on any error
                var valid = true;
                $scope.model.errors = [];

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

                // Name, project, and staining are all required
                if ($scope.model.current_staining == null || $scope.model.panel_name == null || $scope.model.current_project == null) {
                    valid = false;
                }

                // For non full-stain panels, a parent panel is required
                var check_parent_params = false;
                if ($scope.model.current_staining != 'FS' && $scope.model.current_staining != null) {
                    if (!$scope.model.parent_template) {
                        $scope.model.errors.push('Please choose a panel template');
                        valid = false;
                        $scope.model.template_valid = valid;
                        return valid;
                    }
                    check_parent_params = true;
                    // reset all project param matches
                    $scope.model.parent_template.parameters.forEach(function (p) {
                        p.match = false;
                    });
                }
                var can_have_uns = null;
                var can_have_iso = null;
                var fluoro_duplicates = [];
                switch ($scope.model.current_staining) {
                    case 'IS':
                        can_have_uns = false;
                        can_have_iso = true;
                        break;
                    default :  // includes FS, FM, & US
                        can_have_uns = true;
                        can_have_iso = false;
                }

                $scope.model.channels.forEach(function (channel) {
                    channel.errors = [];
                    // check for function
                    if (!channel.function) {
                        channel.errors.push('Function is required');
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
                        if (!channel.fluorochrome && !channel.markers.length > 0) {
                            channel.errors.push("Fluorescence conjugated marker channels must " +
                        "specify either a fluorochrome or at least more than one marker (or both a fluorochrome and markers)");
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

                    // For non full-stain templates, match against the parent's
                    // parameters starting with the function / value type combo
                    if (check_parent_params) {
                        for (var i = 0; i < $scope.model.parent_template.parameters.length; i++) {
                            // param var is just for better readability
                            var param = $scope.model.parent_template.parameters[i];

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
                    }
                });

                if (check_parent_params) {
                    $scope.model.parent_template.parameters.forEach(function (p) {
                        if (!p.match) {
                            valid = false;
                        }
                    });
                }

                $scope.model.template_valid = valid;
                return valid;
            };

            $scope.savePanel = function () {
                var is_valid = $scope.validatePanel();

                if (!is_valid) {
                    return;
                }

                var params = [];
                $scope.model.channels.forEach(function (c) {
                    if (!c.value_type) {
                        c.value_type = null;
                    }
                    params.push({
                        parameter_type: c.function,
                        parameter_value_type: c.value_type,
                        markers: c.markers,
                        fluorochrome: c.fluorochrome || null
                    })
                });
                var parent_template_id = null;
                if ($scope.model.parent_template) {
                    parent_template_id = $scope.model.parent_template.id;
                }
                var data = {
                    panel_name: $scope.model.panel_name,
                    project: $scope.model.current_project,
                    staining: $scope.model.current_staining,
                    parent_panel: parent_template_id,
                    parameters: params,
                    panel_description: ""
                };
                if ($scope.model.template) {
                    var panel_template = ProjectPanel.update({id: template_id}, data);
                } else {
                    var panel_template = ProjectPanel.save(data);
                }
                panel_template.$promise.then(function (o) {
                    // re-direct to project's Panel template list
                    $window.location = '/project/' + $scope.model.current_project + '/templates/';
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
            // everything but bead functions
            $scope.model.parameter_functions = [
                ["FSC", "Forward Scatter"],
                ["SSC", "Side Scatter"],
                ["BEA", "Bead"],
                ["FCM", "Fluorochrome Conjugated Marker"],
                ["UNS", "Unstained"],
                ["ISO", "Isotype Control"],
                ["EXC", "Exclusion"],
                ["VIA", "Viability"],
                ["TIM", "Time"],
                ["NUL", "Null"]
            ];
            $scope.model.parameter_value_types = ParameterValueType.query();
        }
    ]
);