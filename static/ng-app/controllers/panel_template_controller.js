app.controller(
    'PanelTemplateController',
    ['$scope', '$controller', 'ModelService', function ($scope, $controller, ModelService) {
        // Inherits ProjectDetailController $scope
        $controller('ProjectDetailController', {$scope: $scope});

        function get_list() {
            var response = ModelService.getPanelTemplates(
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
        }

        $scope.$on('current_project:updated', function () {
            $scope.panel_templates = get_list();
        });

        $scope.$on('panel_templates:updated', function () {
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

            var response = ModelService.createUpdatePanelTemplate(new_panel);

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
        '$scope', '$state', '$controller', '$stateParams', '$timeout', 'ModelService',
        function ($scope, $state, $controller, $stateParams, $timeout, ModelService) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            $scope.model = {};
            $scope.model.markers = ModelService.getMarkers();
            $scope.model.fluorochromes = ModelService.getFluorochromes();
            $scope.model.parameter_value_types = ModelService.getParameterValueTypes();

            $scope.model.panel_template_types = [
                ["FS", "Full Stain"],
                ["US", "Unstained"],
                ["FM", "Fluorescence Minus One"],
                ["IS", "Isotype Control"],
                ["CB", "Compensation Bead"]
            ];

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

            $scope.model.parameter_errors = [];
            $scope.model.template_valid = false;

            // may be trying to edit an existing template
            // Note: had to add a timeout here b/c existing markers wouldn't
            // show up in the view, and $scope.$apply() causes a
            // $rootScope:inprog error. Not happy with this.
            $timeout(function () {
                if ($stateParams.hasOwnProperty('templateID')) {
                    var template_id = parseInt($stateParams.templateID);
                    $scope.model.template = ModelService.getPanelTemplate(
                        template_id
                    );

                    $scope.model.template.$promise.then(function () {
                        $scope.model.panel_name = $scope.model.template.panel_name;
                        $scope.model.current_staining = $scope.model.template.staining;
                        $scope.model.panel_templates = ModelService.getPanelTemplates(
                            {
                                project: $scope.current_project.id,
                                staining: ['FS']  // only full stain can be parents
                            }
                        );

                        $scope.model.panel_templates.$promise.then(function () {
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
                        }, function (error) {
                            $scope.errors = error.data;
                        });

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
                    }, function (error) {
                        $scope.errors = error.data;
                    });
                } else {
                    $scope.model.parent_template = null;
                    $scope.model.channels = [{markers: []}];
                    // get all project's panel templates matching full stain
                    $scope.model.panel_templates = ModelService.getPanelTemplates(
                        {
                            project: $scope.current_project.id,
                            staining: ['FS']  // only full stain can be parents
                        }
                    );
                }
            }, 100);

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

            $scope.addChannel = function() {
                $scope.model.channels.push({markers:[]});
                $scope.validatePanel();
            };

            $scope.removeChannel = function(channel) {
                $scope.model.channels.splice($scope.model.channels.indexOf(channel), 1);
                $scope.validatePanel();
            };

            $scope.validatePanel = function() {
                /*
                Validation rules:
                    - existing templates w/site panels cannot be edited
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

                // start with true and set to false on any error
                var valid = true;
                $scope.model.errors = [];

                // existing templates w/related site panels cannot be edited
                if ($scope.model.template) {
                    if ($scope.model.template.hasOwnProperty('id')) {
                        if ($scope.model.template.site_panel_count > 0) {
                            $scope.model.errors.push(
                                'This template has existing Sample Annotations, and cannot be edited.'
                            );
                            valid = false;
                            $scope.model.template_valid = valid;
                            return valid;
                        }
                    }
                }

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
                }

                var can_have_uns = null;
                var can_have_iso = null;
                var fluoro_duplicates = [];
                var channel_duplicates = [];
                var fmo_match_count = 0;
                var iso_match_count = 0;

                switch ($scope.model.current_staining) {
                    case 'IS':
                        can_have_uns = false;
                        can_have_iso = true;
                        break;
                    case 'CB':
                        can_have_uns = false;
                        can_have_iso = false;
                        break;
                    default :  // includes FS, FM, & US
                        can_have_uns = true;
                        can_have_iso = false;
                }

                // for checking against parent template parameters later (only for non-FS panels)
                var scatter_channels = [];
                var fcm_channels = [];  // fluoro conjugated marker channels
                var unstained_channels = [];
                var iso_channels = [];
                var exclude_channels = [];
                var viability_channels = [];
                var bead_channels = [];
                var time_channels = [];

                $scope.model.channels.forEach(function (channel) {
                    channel.errors = [];
                    // Function type is required for all channels
                    if (!channel.function) {
                        valid = false;
                        $scope.model.template_valid = valid;
                        return valid;
                    }

                    // Only time channels can have value type 'T'
                    if (channel.function != 'TIM' && channel.value_type == 'T') {
                        channel.errors.push('Only Time channels can have time value type')
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

                    // Check for fluoro duplicates
                    if (channel.fluorochrome) {
                        if (fluoro_duplicates.indexOf(channel.fluorochrome.toString() + "_" + channel.value_type) >= 0) {
                            channel.errors.push('The same fluorochrome cannot be in multiple channels');
                        } else {
                            fluoro_duplicates.push(channel.fluorochrome.toString() + "_" + channel.value_type);
                        }
                    }

                    // Scatter channels
                    if (channel.function == 'FSC' || channel.function == 'SSC') {
                        scatter_channels.push(channel);

                        // ensure no fluoro or markers in scatter channels
                        if (channel.fluorochrome) {
                            channel.errors.push('Scatter channels cannot have a fluorochrome');
                        }
                        if (channel.markers.length > 0) {
                            channel.errors.push('Scatter channels cannot have markers');
                        }
                    } else if (channel.function == 'UNS') {  // Unstained channels (used for FMO channels)
                        unstained_channels.push(channel);

                        if (!can_have_uns && channel.function == 'UNS') {
                            channel.errors.push($scope.model.current_staining + ' panels cannot have unstained channels');
                        }

                        // unstained channels cannot have a fluoro but must have at least 1 marker
                        if (channel.fluorochrome) {
                            channel.errors.push('Unstained channels cannot specify a fluorochrome');
                        }
                        if (channel.markers.length < 1) {
                            channel.errors.push('Unstained channels must specify at least one marker');
                        }
                    } else if (channel.function == 'ISO') {  // ISO channels
                        iso_channels.push(channel);

                        if (!can_have_iso) {
                            channel.errors.push('Only Iso panels can include iso channels');
                        }

                        // Iso channels must have a fluoro, cannot have an Ab
                        if (!channel.fluorochrome) {
                            channel.errors.push('Iso channels must specify a fluorochrome');
                        }
                        if (channel.markers.length > 0) {
                            channel.errors.push('Iso channels cannot have markers');
                        }
                    } else if (channel.function == 'EXC') {
                        exclude_channels.push(channel);

                        // exclusion channels must include a fluoro
                        if (!channel.fluorochrome) {
                            channel.errors.push('Exclusion channels must specify a fluorochrome');
                        }
                    } else if (channel.function == 'FCM') {
                        fcm_channels.push(channel);

                        // fluoro conjugate channels must have both fluoro and Ab
                        if (!channel.fluorochrome && !channel.markers.length > 0) {
                            channel.errors.push("Fluorescence conjugated marker channels must " +
                        "specify either a fluorochrome or at least more than one marker (or both a fluorochrome and markers)");
                        }
                    } else if (channel.function == 'BEA') {
                        bead_channels.push(channel);

                        // Bead channels must specify a fluoro but no marker
                        if (!channel.fluorochrome) {
                            channel.errors.push('Bead channels must specify a fluorochrome');
                        }
                        if (channel.markers.length > 0) {
                            channel.errors.push('Bead channels cannot have markers');
                        }
                    } else if (channel.function == 'TIM') {
                        time_channels.push(channel);

                        // Time channels cannot have a fluoro or Ab, must have value type 'T'
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

                    if (channel.errors.length > 0 ) {
                        valid = false;
                    }
                });

                // For non full-stain templates, ensure channels match parent's parameters.
                if (check_parent_params) {
                    // iterate over every parent template parameter
                    for (var i = 0; i < $scope.model.parent_template.parameters.length; i++) {
                        // We need to compare the channel function types in a particular order to
                        // correctly match FMO & ISO parameters in the parent template.
                        // We'll start with the other categories and match in this order:
                        //   - scatter channels
                        //   - fluoro conjugated channels
                        //   -

                        // param var just to make code shorter and easier to read
                        var param = $scope.model.parent_template.parameters[i];

                        // assume no match, we'll mark them true as we find them
                        param.match = false;
                        param.fmo_match = false;
                        param.iso_match = false;
                        var marker_match;

                        // check against all the parent scatter params first
                        if (param.parameter_type == 'FSC' || param.parameter_type == 'SSC') {
                            for (var j=0; j < scatter_channels.length; j++) {
                                // if value type doesn't match, then it can't be a match
                                if (param.parameter_value_type != scatter_channels[j].value_type) {
                                    // no match
                                    continue;
                                }
                                if (param.parameter_type == scatter_channels[j].parameter_type) {
                                    param.match = true;
                                    break;
                                }
                            }
                            continue;
                        }

                        // next, the parent's viability params
                        if (param.parameter_type == 'VIA') {
                            // first check against the proposed panel's FCM channels
                            for (var j=0; j < viability_channels.length; j++) {
                                // if value type doesn't match, then it can't be a match
                                if (param.parameter_value_type != viability_channels[j].value_type) {
                                    // no match
                                    continue;
                                }

                                // verify parent's fluoro is matched
                                if (param.fluorochrome) {
                                    if (param.fluorochrome != viability_channels[j].fluorochrome) {
                                        // no match
                                        continue;
                                    }
                                }

                                // verify all parent's markers are present
                                marker_match = true;
                                for (var k = 0; k < param.markers.length; k++) {
                                    if (viability_channels[j].markers.indexOf(param.markers[k].marker_id) == -1) {
                                        // no match
                                        marker_match = false;
                                        break;
                                    }
                                }
                                if (marker_match) {
                                    // if we get here everything matched and we're done with param
                                    param.match = true;
                                    break;
                                }
                            }

                            // A viability param may match a bead channel in the
                            // proposed panel, but only for proposed bead templates
                            if ($scope.model.current_staining == 'CB') {
                                for (var j=0; j < bead_channels.length; j++) {
                                    // if value type doesn't match, then it can't be a match
                                    if (param.parameter_value_type != bead_channels[j].value_type) {
                                        // no match
                                        continue;
                                    }

                                    // bead channels don't have markers so only verify fluoro
                                    if (param.fluorochrome) {
                                        if (param.fluorochrome == iso_channels[j].fluorochrome) {
                                            // MATCH!
                                            param.match = true;
                                            param.bead_match = true;
                                            bead_match_count++;
                                            break;
                                        }
                                    }
                                }
                            }
                            continue;
                        }

                        // next, the parent's fluoro conjugated marker params
                        if (param.parameter_type == 'FCM') {
                            // first check against the proposed panel's FCM channels
                            for (var j=0; j < fcm_channels.length; j++) {
                                // if value type doesn't match, then it can't be a match
                                if (param.parameter_value_type != fcm_channels[j].value_type) {
                                    // no match
                                    continue;
                                }

                                // verify parent's fluoro is matched
                                if (param.fluorochrome) {
                                    if (param.fluorochrome != fcm_channels[j].fluorochrome) {
                                        // no match
                                        continue;
                                    }
                                }

                                // verify all parent's markers are present
                                marker_match = true;
                                for (var k = 0; k < param.markers.length; k++) {
                                    if (fcm_channels[j].markers.indexOf(param.markers[k].marker_id) == -1) {
                                        // no match
                                        marker_match = false;
                                        break;
                                    }
                                }
                                if (marker_match) {
                                    // if we get here everything matched and we're done with param
                                    param.match = true;
                                    break;
                                }
                            }

                            if (param.match) {
                                continue;
                            }

                            // Our parent's FCM param may match an UNS channel in the
                            // proposed panel
                            for (var j=0; j < unstained_channels.length; j++) {
                                // if value type doesn't match, then it can't be a match
                                if (param.parameter_value_type != unstained_channels[j].value_type) {
                                    // no match
                                    continue;
                                }

                                // unstained channels don't have fluoros so only verify markers
                                marker_match = true;
                                for (var k = 0; k < param.markers.length; k++) {
                                    if (unstained_channels[j].markers.indexOf(param.markers[k].marker_id) == -1) {
                                        // no match
                                        marker_match = false;
                                        break;
                                    }
                                }
                                if (marker_match) {
                                    // if we get here everything matched and we're done with param
                                    param.match = true;
                                    param.fmo_match = true;
                                    fmo_match_count++;

                                    // remove match from fmo candidates
                                    unstained_channels.splice(j, 1);
                                    j--;

                                    break;
                                }

                            }

                            if (param.match) {
                                continue;
                            }

                            // Likewise, the parent's FCM param may match an ISO channel in the
                            // proposed panel
                            for (var j=0; j < iso_channels.length; j++) {
                                // if value type doesn't match, then it can't be a match
                                if (param.parameter_value_type != iso_channels[j].value_type) {
                                    // no match
                                    continue;
                                }

                                // iso channels don't have markers so only verify fluoro
                                if (param.fluorochrome) {
                                    if (param.fluorochrome == iso_channels[j].fluorochrome) {
                                        // MATCH!
                                        param.match = true;
                                        param.iso_match = true;
                                        iso_match_count++;

                                        // remove match from iso candidates
                                        iso_channels.splice(j, 1);
                                        j--;

                                        break;
                                    }
                                }
                            }

                            if (param.match) {
                                continue;
                            }

                            // Finally, the FCM param may match a bead channel in the
                            // proposed panel, but only for proposed bead templates
                            if ($scope.model.current_staining == 'CB') {
                                for (var j=0; j < bead_channels.length; j++) {
                                    // if value type doesn't match, then it can't be a match
                                    if (param.parameter_value_type != bead_channels[j].value_type) {
                                        // no match
                                        continue;
                                    }

                                    // bead channels don't have markers so only verify fluoro
                                    if (param.fluorochrome) {
                                        if (param.fluorochrome == iso_channels[j].fluorochrome) {
                                            // MATCH!
                                            param.match = true;
                                            param.bead_match = true;
                                            bead_match_count++;
                                            break;
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                if ($scope.model.current_staining == 'FM' && fmo_match_count < 1) {
                    valid = false;
                    $scope.model.errors.push("FMO templates must specify at least one unstained channel.");
                } else if ($scope.model.current_staining == 'IS' && iso_match_count < 1) {
                    valid = false;
                    $scope.model.errors.push("ISO templates must specify at least one ISO channel.");
                }

                // if all parent params do not match,
                // the proposed panel is invalid
                $scope.model.parent_template.parameters.forEach(function (param) {
                    if (!param.match) {
                        valid = false;
                    }
                });
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
                    data.id = $scope.model.template.id;
                }
                var panel_template = ModelService.createUpdatePanelTemplate(
                    data
                );

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