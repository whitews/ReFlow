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

            $scope.validatePanel = function() {
                $scope.model.errors = [];

                if (!$scope.model.current_project_panel) {
                    $scope.model.errors.push('Please choose a project panel');
                    return;
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
                Validations against the parent project panel:
                    - Ensure all project panel parameters are present
                */
                var staining = $scope.model.current_project_panel.staining;
                var can_have_uns = null;
                var can_have_iso = null;
                switch (staining) {
                    case 'IS':
                        can_have_uns = false;
                        can_have_iso = true;
                        break;
                    default :  // includes FS, FM, & US
                        can_have_uns = true;
                        can_have_iso = false;
                }

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
                });
            };

            $scope.savePanel = function () {
                console.log($scope.model.current_project_panel.name);
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
            $scope.model.project_panels = ProjectPanel.query(
                {
                    project: $scope.model.current_project.id
                }
            );
            $scope.model.site_panel_sample = f;

            $scope.model.site_panel_sample.channels.forEach(function (c) {
                c.function = null;

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
                        if (jQuery.inArray(m.marker_abbreviation, words) >= 0) {
                            c.markers.push(m.id);
                        }
                    });

                    // for the fluorochromes, matching is a bit tricky b/c of tandem dyes
                    // we'll need to check against the longest match in the entire
                    // fcs_text first and then the words
                    var fl_match = '';
                    $scope.model.fluorochromes.forEach(function(f) {
                        if (c.pnn.indexOf(f.fluorochrome_abbreviation) >= 0) {
                            if (f.fluorochrome_abbreviation.length > fl_match.length) {
                                fl_match = f.fluorochrome_abbreviation;
                                c.fluorochrome = f.id;
                            }
                        } else if (c.pns.indexOf(f.fluorochrome_abbreviation) >= 0) {
                            if (f.fluorochrome_abbreviation.length > fl_match.length) {
                                fl_match = f.fluorochrome_abbreviation;
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