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
            $scope.model.markers = ModelService.getMarkers($scope.current_project.id);
            $scope.model.fluorochromes = ModelService.getFluorochromes($scope.current_project.id);
            $scope.model.parameter_value_types = ModelService.getParameterValueTypes();

            // everything but bead functions
            $scope.model.parameter_functions = [
                ["FSC", "Forward Scatter"],
                ["SSC", "Side Scatter"],
                ["FLR", "Fluorescence"],
                ["TIM", "Time"]
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
                    }, function (error) {
                        $scope.errors = error.data;
                    });
                } else {
                    $scope.model.channels = [{markers: []}];
                }
            }, 100);

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

                // Name, project are required
                if ($scope.model.panel_name == null || $scope.current_project == null) {
                    valid = false;
                }

                var fluoro_duplicates = [];
                var channel_duplicates = [];

                $scope.model.channels.forEach(function (channel) {
                    channel.errors = [];
                    // Function type is required for all channels
                    if (!channel.function || !channel.value_type) {
                        channel.errors.push('All channels must specify a function and a value type')
                        valid = false;
                        $scope.model.template_valid = valid;
                        return valid;
                    }

                    // Only time channels can have value type 'T'
                    if (channel.function != 'TIM' && channel.value_type == 'T') {
                        channel.errors.push('Only Time channels can have time value type')
                    }

                    // Check for duplicate channels
                    // For fluoro channels we don't consider value type b/c
                    // mixed value type fluoro channels cause issues wiht the
                    // automated analysis (mainly compensation). For scatter
                    // channels we need to use the value type to prevent
                    // "pure" duplicate scatter channels.
                    if (channel.function == 'FSC' || channel.function == 'SSC') {
                        var channel_string = [
                            channel.function,
                            channel.value_type,
                            channel.markers.sort().join("-"),
                            channel.fluorochrome
                        ].join("_");
                    } else {
                        var channel_string = [
                            channel.function,
                            channel.markers.sort().join("-"),
                            channel.fluorochrome
                        ].join("_");
                    }
                    if (channel_duplicates.indexOf(channel_string) >= 0) {
                        channel.errors.push('Duplicate channels are not allowed');
                    } else {
                        channel_duplicates.push(channel_string);
                    }

                    // Check for fluoro duplicates
                    if (channel.fluorochrome) {
                        if (fluoro_duplicates.indexOf(channel.fluorochrome.toString()) >= 0) {
                            channel.errors.push('The same fluorochrome cannot be in multiple channels');
                        } else {
                            fluoro_duplicates.push(channel.fluorochrome.toString());
                        }
                    }

                    // Scatter channels
                    if (channel.function == 'FSC' || channel.function == 'SSC') {
                        // ensure no fluoro or markers in scatter channels
                        if (channel.fluorochrome) {
                            channel.errors.push('Scatter channels cannot have a fluorochrome');
                        }
                        if (channel.markers.length > 0) {
                            channel.errors.push('Scatter channels cannot have markers');
                        }
                    } else if (channel.function == 'FLR') {
                        // fluoro conjugate channels must have a fluoro
                        if (!channel.fluorochrome && channel.markers.length < 1) {
                            channel.errors.push("Fluorescence parameters must " +
                        "specify either a marker or a fluorochrome (or both)");
                        }
                    } else if (channel.function == 'BEA') {
                        // Bead channels must specify a fluoro but no marker
                        if (!channel.fluorochrome) {
                            channel.errors.push('Bead channels must specify a fluorochrome');
                        }
                        if (channel.markers.length > 0) {
                            channel.errors.push('Bead channels cannot have markers');
                        }
                    } else if (channel.function == 'TIM') {
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

                var data = {
                    panel_name: $scope.model.panel_name,
                    project: $scope.current_project.id,
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