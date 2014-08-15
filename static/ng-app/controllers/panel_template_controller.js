app.controller(
    'PanelTemplateController',
    ['$scope', '$controller', 'PanelTemplate', function ($scope, $controller, PanelTemplate) {
        // Inherits ProjectDetailController $scope
        $controller('ProjectDetailController', {$scope: $scope});

        function get_list() {
            var response = PanelTemplate.query(
                {
                    'project': $scope.current_project.id
                }
            );

            $scope.expand_params = [];
            response.$promise.then(function (panel_templates) {
                panel_templates.forEach(function () {
                    $scope.expand_params.push(false);
                })
            });
            return response;
        }

        if ($scope.current_project != undefined) {
            $scope.panel_templates = get_list();
        } else {
            $scope.$on('currentProjectSet', function () {
                $scope.panel_templates = get_list();
            });
        }

        $scope.$on('updatePanelTemplates', function () {
            $scope.panel_templates = get_list();
        });

        $scope.toggle_params = function (i) {
            $scope.expand_params[i] = $scope.expand_params[i] != true;
        };

        $scope.expand_all_panels = function () {
            for (var i = 0; i < $scope.panel_templates.length; i++) {
                $scope.expand_params[i] = true;
            }
        };

        $scope.collapse_all_panels = function () {
            for (var i = 0; i < $scope.panel_templates.length; i++) {
                $scope.expand_params[i] = false;
            }
        };

        $scope.copy_panel = function (panel) {
            var new_panel = angular.copy(panel);

            delete new_panel.id;
            new_panel.panel_name = new_panel.panel_name + ' [copy]';

            new_panel.parameters.forEach(function(param) {
                delete param.id;
                var markers = [];
                param.markers.forEach(function(m) {
                    markers.push(m.marker_id);
                });
                param.markers = markers;
            });

            var response = PanelTemplate.save(new_panel);

            response.$promise.then(function() {
                $scope.panel_templates = get_list();
            }, function (error) {
                $scope.errors = error.data;
            });
        };
    }
]);

app.controller(
    'PanelTemplateCreateController',
    [
        '$scope', '$state', '$controller', '$stateParams', 'PanelTemplate', 'Marker', 'Fluorochrome',
        function ($scope, $state, $controller, $stateParams, PanelTemplate, Marker, Fluorochrome) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.model = {};
            $scope.model.markers = Marker.query();
            $scope.model.fluorochromes = Fluorochrome.query();

            $scope.model.panel_template_types = [
                ["FS", "Full Stain"],
                ["US", "Unstained"],
                ["FM", "Fluorescence Minus One"],
                ["IS", "Isotype Control"],
                ["CB", "Compensation Bead"]
            ];

            $scope.model.parameter_errors = [];
            $scope.model.template_valid = false;

            function findFluoroByID(id) {
                for (var i = 0; i < $scope.model.fluorochromes.length; i++) {
                    if ($scope.model.fluorochromes[i].id === id) {
                        return $scope.model.fluorochromes[i].fluorochrome_abbreviation;
                    }
                }
            }

            // may be trying to edit an existing template
            if ($stateParams.templateID) {
                var template_id = $stateParams.templateID;
                $scope.model.template = PanelTemplate.get(
                    {id: template_id},
                    function () {
                        $scope.model.panel_name = $scope.model.template.panel_name;
                        $scope.model.current_staining = $scope.model.template.staining;
                        $scope.model.panel_templates = PanelTemplate.query(
                            {
                                project: $scope.current_project,
                                staining: ['FS']  // only full stain can be parents
                            },
                            function () {
                                if ($scope.model.template.parent_panel) {
                                    $scope.model.parent_template_required = true;
                                    for (var i = 0; i < $scope.model.panel_templates.length; i++) {
                                        if ($scope.model.panel_templates[i].id == $scope.model.template.parent_panel) {
                                            $scope.model.parent_template = $scope.model.panel_templates[i];
                                            $scope.validatePanel();
                                            break;
                                        }
                                    }
                                }
                            }
                        );

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
                                    channel.markers.push(m.marker_id.toString());
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

            $scope.stainingChanged = function() {
                // check if a parent is required
                if ($scope.model.current_staining) {
                    if ($scope.model.current_staining != 'FS') {
                        $scope.model.parent_template_required = true;
                    } else {
                        $scope.model.parent_template_required = false;
                    }
                } else {
                    $scope.model.parent_template_required = false;
                }
                $scope.validatePanel();
            };

            // get all project's panel templates matching full stain
            $scope.model.panel_templates = PanelTemplate.query(
                {
                    project: $scope.current_project.id,
                    staining: ['FS']  // only full stain can be parents
                }
            );

            $scope.addChannel = function() {
                $scope.model.channels.push({markers:[]});
                $scope.validatePanel();
            };

            $scope.removeChannel = function(channel) {
                $scope.model.channels.splice($scope.model.channels.indexOf(channel), 1);
                $scope.validatePanel();
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
                    - FMO templates must specify an UNS channel
                    - ISO templates must specify an ISO channel
                */

                // Name, project, and staining are all required
                if ($scope.model.current_staining == null || $scope.model.panel_name == null || $scope.current_project == null) {
                    valid = false;
                }

                // For non full-stain panels, a parent panel is required
                var check_parent_params = false;
                if ($scope.model.current_staining != 'FS' && $scope.model.current_staining != null) {
                    if (!$scope.model.parent_template) {
                        $scope.model.errors.push(
                            'Please choose the associated Full Stain parent template'
                        );
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
                var channel_duplicates = [];
                var parent_iso_matches = [];
                var parent_fmo_matches = [];
                switch ($scope.model.current_staining) {
                    case 'IS':
                        can_have_uns = false;
                        can_have_iso = true;
                        break;
                    case 'CB':
                        can_have_uns = false;
                        can_have_iso = false;
                    default :  // includes FS, FM, & US
                        can_have_uns = true;
                        can_have_iso = false;
                }

                $scope.model.channels.forEach(function (channel) {
                    channel.errors = [];
                    // check for function
                    if (!channel.function) {
                        valid = false;
                        $scope.model.template_valid = valid;
                        return valid;
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
                        channel.errors.push($scope.model.current_staining + ' panels cannot have unstained channels');
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

                    // Bead channels must specify a fluoro but no marker
                    if (channel.function == 'BEA') {
                        if (!channel.fluorochrome) {
                            channel.errors.push('Bead channels must specify a fluorochrome');
                        }
                        if (channel.markers.length > 0) {
                            channel.errors.push('Bead channels cannot have markers');
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
                    } else {
                        if (channel.value_type == 'T') {
                            channel.errors.push('Only Time channels can have time value type')
                        }
                    }

                    // Check for duplicate channels
                    var channel_string = [
                        channel.function,
                        channel.value_type,
                        channel.markers.sort().join("-"),
                        channel.fluorochrome
                    ].join("_");
                    if (channel_duplicates.indexOf(channel_string) >= 0) {
                        channel.errors.push('Duplicate channels are not allowed');
                    } else {
                        channel_duplicates.push(channel_string);
                    }


                    // For non full-stain templates, match against the parent's
                    // parameters starting with the function / value type combo
                    if (check_parent_params) {
                        for (var i = 0; i < $scope.model.parent_template.parameters.length; i++) {
                            // param var is just for better readability
                            var param = $scope.model.parent_template.parameters[i];
                            var fmo_match = false;
                            var iso_match = false;

                            // first, check function
                            if (param.parameter_type != channel.function) {
                                // but it's not so simple, we need to allow
                                // FMO panels to have unstained counterparts to
                                // their parent Full stain template.
                                // Likewise, Isotype Control templates can
                                // have ISO channel counterparts.

                                // However, first we'll check the easy things
                                // like scatter channels
                                if (channel.function == 'FSC' && param.parameter_type != 'FSC') {
                                    // no match
                                    continue;
                                } else if (channel.function == 'SSC' && param.parameter_type != 'SSC') {
                                    // no match
                                    continue;
                                }

                                if ($scope.model.current_staining == 'FM') {
                                    if (param.parameter_type == 'FCM' && channel.function == 'UNS') {
                                        fmo_match = true;
                                    } else {
                                        // no match
                                        continue;
                                    }
                                } else if ($scope.model.current_staining == 'IS') {
                                    if (param.parameter_type == 'FCM' && channel.function == 'ISO') {
                                        iso_match = true;
                                    } else {
                                        // no match
                                        continue;
                                    }
                                } else if ($scope.model.current_staining == 'CB') {
                                    // For bead templates the function should
                                    // be bead
                                    if (param.parameter_type != 'FCM' && channel.function == 'BEA') {
                                        // no match
                                        continue;
                                    }
                                } else {
                                    // no match
                                    continue;
                                }
                            }

                            // then value type
                            if (param.parameter_value_type != channel.value_type) {
                                // no match
                                continue;
                            }

                            // if template has fluoro, check it, except for
                            // unstained channels
                            if (param.fluorochrome && channel.function != 'UNS') {
                                if (param.fluorochrome != channel.fluorochrome) {
                                    // no match
                                    continue;
                                }
                            }

                            // Bead channels must have a fluoro, or it cannot
                            // be any match
                            if (channel.function == 'BEA' && !channel.fluorochrome) {
                                // no match
                                break;
                            }

                            // if template has markers, check them all, except
                            // for ISO and Bead channels
                            if (param.markers.length > 0) {
                                if (channel.function != 'ISO' && channel.function != 'BEA') {
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
                            }

                            // if we get here everything in the template matched
                            param.match = true;

                            // and save iso/fmo matches
                            if (fmo_match) {
                                parent_fmo_matches.push(i);
                            }

                            if (iso_match) {
                                parent_iso_matches.push(i);
                            }
                        }
                    }

                    if (channel.errors.length > 0 ) {
                        valid = false;
                    }
                });

                if (check_parent_params) {
                    for (var i = 0; i < $scope.model.parent_template.parameters.length; i++) {
                        if (!$scope.model.parent_template.parameters[i].match) {
                            valid = false;
                        }
                        if (parent_fmo_matches.indexOf(i) > -1) {
                            $scope.model.parent_template.parameters[i].fmo_match = true;
                        } else {
                            $scope.model.parent_template.parameters[i].fmo_match = false;
                        }
                        if (parent_iso_matches.indexOf(i) > -1) {
                            $scope.model.parent_template.parameters[i].iso_match = true;
                        } else {
                            $scope.model.parent_template.parameters[i].iso_match = false;
                        }
                    }
                }

                if ($scope.model.current_staining == 'FM' && parent_fmo_matches < 1) {
                    valid = false;
                    $scope.model.errors.push("FMO templates must specify at least one unstained channel.");
                } else if ($scope.model.current_staining == 'IS' && parent_iso_matches < 1) {
                    valid = false;
                    $scope.model.errors.push("ISO templates must specify at least one ISO channel.");
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
                    project: $scope.current_project.id,
                    staining: $scope.model.current_staining,
                    parent_panel: parent_template_id,
                    parameters: params,
                    panel_description: ""
                };
                if ($scope.model.template) {
                    var panel_template = PanelTemplate.update({id: template_id}, data);
                } else {
                    var panel_template = PanelTemplate.save(data);
                }
                panel_template.$promise.then(function (o) {
                    // change to project's Panel template list
                    $state.go('panel-template-list')
                }, function(error) {
                    $scope.model.errors = [];
                    for (var key in error.data) {
                        if (error.data.hasOwnProperty(key)) {
                            if (error.data[key] instanceof Array) {
                                $scope.model.errors.push.apply(
                                    $scope.model.errors, error.data[key]
                                );
                            } else {
                                $scope.model.errors.push(error.data[key]);
                            }
                        }
                    }
                });
            };
        }
    ]
);

app.controller(
    'TemplateParameterController',
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