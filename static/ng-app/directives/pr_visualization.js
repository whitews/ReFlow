app.directive('prvisualization', function() {
    return {
        controller: 'PRVisualizationController',
        restrict: 'E',
        replace: true,
        templateUrl: 'static/ng-app/directives/pr_visualization.html',
        scope: {
            data: '='
        }
    };
});

app.controller(
    'PRVisualizationController',
    [
        '$scope',
        '$q',
        '$modal',
        'ModelService',
        function ($scope, $q, $modal, ModelService) {
            var sample_clusters = null;
            var panel_data = null;

            // Cell subset label variables for tagging clusters
            if (ModelService.current_project) {
                $scope.labels = ModelService.getCellSubsetLabels(
                    ModelService.current_project.id
                );
            }
            $scope.$on('current_project:updated', function () {
                $scope.labels = ModelService.getCellSubsetLabels(
                    ModelService.current_project.id
                );
            });

            $scope.$watch('data', function(data) {
                // first sort data.members by the sample's original_filename
                if (data != undefined && data.hasOwnProperty("members")) {
                    data.members.sort(function (a, b) {
                        if (a.sample.original_filename < b.sample.original_filename) {
                            return -1;
                        } else if (a.sample.original_filename > b.sample.original_filename) {
                            return 1;
                        } else {
                            return 0;
                        }
                    });
                }

                $scope.sample_collection = data;
                $scope.cached_plots = {};
            });

            function get_analyzed_parameters(parameters, example_cluster) {
                /*
                 Determine analyzed parameters, as not all parameters
                 may have been analyzed. We only need to copy the
                 'fcs_number' and the 'full_text' properties. This is
                 used for the parallel plot and for the initial selection
                 of scatterplot x & y parameters

                 Arguments:
                    parameters: current list of site panel parameter objects
                    example_cluster: an example cluster that will contain
                                     only the analyzed channel numbers
                 */
                var analyzed_parameters = [];
                parameters.forEach(function (param) {
                    // use the cluster params for comparison
                    for (var i = 0; i < example_cluster.parameters.length; i++) {
                        if (param.fcs_number == example_cluster.parameters[i].channel) {
                            analyzed_parameters.push(param);
                            break;
                        }
                    }
                });

                return analyzed_parameters;
            }

            $scope.initialize_visualization = function() {
                // May be "re-initializing" the vis so remember any expanded
                // clusters so we can "re-expand" them in the new sample
                var expanded_cluster_indices = [];
                if ($scope.hasOwnProperty('plot_data')) {
                    $scope.plot_data.cluster_data.forEach(function (c) {
                        if (c.display_events) {
                            expanded_cluster_indices.push(c.cluster_index);
                        }
                    });
                }

                if ($scope.chosen_member.id in $scope.cached_plots) {
                    $scope.plot_data = $scope.cached_plots[$scope.chosen_member.id];

                    $scope.analyzed_parameters = get_analyzed_parameters(
                        $scope.plot_data.panel_data.parameters,
                        $scope.plot_data.cluster_data[0]
                    );

                    // Need to init the parallel plot first so we can
                    // "bold" the expanded clusters
                    $scope.initialize_parallel_plot(
                        $scope.analyzed_parameters,
                        $scope.plot_data.cluster_data
                    );

                    // turn on display_events for originally expanded clusters
                    $scope.plot_data.cluster_data.forEach(function(c) {
                        if (expanded_cluster_indices.indexOf(c.cluster_index) != -1) {
                            c.display_events = true;
                            $scope.select_cluster_line(c);

                            if (c.events_retrieved == false) {
                                $scope.process_cluster_events(c);
                            }
                        } else {
                            c.display_events = false;
                        }
                    });

                    $scope.initialize_scatterplot(true);

                    return;
                }

                $scope.retrieving_data = true;
                $scope.has_parent_stage = $scope.$parent.process_request.parent_stage > 0;
                sample_clusters = ModelService.getSampleClusters(
                    $scope.$parent.process_request.id,
                    $scope.chosen_member.sample.id
                );

                panel_data = ModelService.getSitePanel(
                    $scope.chosen_member.sample.site_panel
                );

                $q.all([sample_clusters, panel_data.$promise]).then(function(data) {
                    $scope.cached_plots[$scope.chosen_member.id] = {
                        'cluster_data': data[0],
                        'panel_data': data[1]
                    };
                    $scope.plot_data = $scope.cached_plots[$scope.chosen_member.id];

                    $scope.analyzed_parameters = get_analyzed_parameters(
                        $scope.plot_data.panel_data.parameters,
                        $scope.plot_data.cluster_data[0]
                    );

                    $scope.initialize_scatterplot(false);
                    $scope.initialize_parallel_plot(
                        $scope.analyzed_parameters,
                        $scope.plot_data.cluster_data
                    );

                    // display events for previously expanded clusters
                    $scope.plot_data.cluster_data.forEach(function(c) {
                        // since the sample is new we can just toggle it
                        if (expanded_cluster_indices.indexOf(c.cluster_index) != -1) {
                            $scope.toggle_cluster_events(c);
                            $scope.select_cluster_line(c);
                        }
                    });
                }).catch(function(e) {
                    // show errors here
                    console.log('error!')
                }).finally(function() {
                    $scope.retrieving_data = false;
                });
            };

            $scope.previous_sample = function() {
                var current_index = $scope.sample_collection.members.indexOf(
                    $scope.chosen_member
                );

                if (current_index === 0) {
                    return;
                } else {
                    $scope.chosen_member = $scope.sample_collection.members[current_index-1];
                    $scope.initialize_visualization();
                }
            };

            $scope.next_sample = function() {
                var current_index = $scope.sample_collection.members.indexOf(
                    $scope.chosen_member
                );

                if (current_index === $scope.sample_collection.members.length - 1) {
                    return;
                } else {
                    $scope.chosen_member = $scope.sample_collection.members[current_index+1];
                    $scope.initialize_visualization();
                }
            };

            $scope.find_matching_parameter = function(param) {
                if (param == null) {
                    return null;
                }
                for (var i = 0; i < $scope.parameters.length; i++) {
                    if (param.full_name === $scope.parameters[i].full_name) {
                        return $scope.parameters[i];
                    }
                }
                return null;
            };

            $scope.parameter_changed = function() {
                $scope.parameter_changed_flag = true;

                if ($scope.auto_transition) {
                    $scope.render_plot();
                }
            };

            /*
            Note: Difference between highlighted, selected, & expanded

            There are 3 different boolean states for each cluster, all of which
            control the look or behaviour of the cluster.

            highlighted:
                Only one of the clusters can be highlighted at any single time,
                and is meant to help identify the cluster in the various
                components (parallel plot, scatter plot, and the data table).
                A cluster is highlighted when the user's mouse cursor hovers
                over either the cluster circle in the scatter-plot OR the
                table row for that cluster in the data table on the right hand
                side of the page. When highlighted the cluster circle is
                larger, the cluster circle is annotated with the cluster index
                & event percentage, the parallel plot line is bolder, and the
                table row background is grey. Highlighting when hovering over
                a cluster circle only works when brush mode is disabled.
            selected:
                Any number of clusters (including zero) can be selected at a
                single time. The only way clusters can be selected is using the
                rectangular brush when the brush mode is enabled. Brush mode
                is controlled by a check-box found above the scatter-plot.
                Cluster selection is intended to be used in conjunction with
                the "expand selected" button and then with the "label expanded"
                button to label multiple clusters at once. The selected state
                looks exactly like the highlighted state (perhaps this should
                be changed?)
            expanded:
                A cluster is expanded when the events for that cluster are
                visible. To expand a cluster the user can either click on the
                cluster circle (when brush mode is disabled) or click the
                check-box in that cluster's row of the data table.
             */

            function pulsate(selection) {
                recursive_transitions();
                function recursive_transitions() {
                    if (selection.data()[0].highlighted) {
                        selection.transition()
                            .duration(400)
                            .attr("r", function (d) {
                                if ($scope.static_cluster_size) {
                                    return 6;
                                } else {
                                    return Math.round(d.event_percentage) + 6;
                                }
                            })
                            .ease('sin-in')
                            .transition()
                            .duration(800)
                            .attr("r", function (d) {
                                if ($scope.static_cluster_size) {
                                    return 12;
                                } else {
                                    return Math.round(d.event_percentage) + 12;
                                }
                            })
                            .ease('bounce-in')
                            .each("end", recursive_transitions);
                    } else {
                        // transition back to normal
                        selection.transition()
                            .duration(200)
                            .attr("r", function (d) {
                                if ($scope.static_cluster_size) {
                                    return 6;
                                } else {
                                    return Math.round(d.event_percentage) + 6;
                                }
                            }
                        );
                    }
                }
            }

            $scope.highlight_cluster = function (cluster) {
                cluster.highlighted = true;

                $scope.clusters.filter(function(d) {
                    if (d.highlighted) {
                        var selected_circles = d3.select(this);
                        pulsate(selected_circles);
                    }
                });

                $scope.select_cluster_line(cluster);
            };

            $scope.dehighlight_cluster = function (cluster) {
                cluster.highlighted = false;

                $scope.clusters.filter(
                    function(d) {
                        if (d.cluster_index == cluster.cluster_index) {
                            return d;
                        }
                    }).attr("r", function(d) {
                        if ($scope.static_cluster_size) {
                            return d.selected ? 10 : 6;
                        } else {
                            return d.selected ? Math.round(d.event_percentage) + 10 : Math.round(d.event_percentage) + 6;
                        }
                    }
                );

                if (!cluster.selected) {
                    $scope.deselect_cluster_line(cluster);
                }
            };

            $scope.select_cluster = function (cluster) {
                cluster.selected = true;

                // visible indicator for selected is a bolder stroke,
                // but we need to differentiate between expanded and
                // non-expanded clusters
                if (cluster.display_events) {
                    $scope.clusters.filter(
                        function (d) {
                            if (d.cluster_index == cluster.cluster_index) {
                                return d;
                            }
                        }
                    ).style("stroke-width", "6");
                } else {
                    $scope.clusters.filter(
                        function (d) {
                            if (d.cluster_index == cluster.cluster_index) {
                                return d;
                            }
                        }
                    ).style("stroke-width", "2.5");
                }

                $scope.select_cluster_line(cluster);
            };

            $scope.deselect_cluster = function (cluster) {
                cluster.selected = false;

                // remove visible indicator for selected state,
                // but we need to differentiate between expanded and
                // non-expanded clusters
                if (cluster.display_events) {
                    $scope.clusters.filter(
                        function (d) {
                            if (d.cluster_index == cluster.cluster_index) {
                                return d;
                            }
                        }
                    ).style("stroke-width", "4");
                } else {
                    $scope.clusters.filter(
                        function (d) {
                            if (d.cluster_index == cluster.cluster_index) {
                                return d;
                            }
                        }
                    ).style("stroke-width", "1.2");
                }

                $scope.deselect_cluster_line(cluster);
            };

            $scope.expand_cluster = function (cluster) {
                $scope.clusters.filter(
                    function(d) {
                        if (d.cluster_index == cluster.cluster_index) {
                            return d;
                        }
                    })
                    .style("stroke-dasharray", "4, 1")
                    .style("stroke-width", "4");
            };

            $scope.collapse_cluster = function (cluster) {
                $scope.clusters.filter(
                    function(d) {
                        if (d.cluster_index == cluster.cluster_index) {
                            return d;
                        }
                    })
                    .style("stroke-dasharray", "1, 0")
                    .style("stroke-width", "1.2");
            };

            function update_cluster_labels(sample_cluster) {
                var response = ModelService.getClusterLabels(
                    {
                        'cluster': sample_cluster.cluster  // the cluster ID
                    }
                );

                response.$promise.then(function (labels) {
                    // success, replace label array for the matching
                    // sample cluster for all samples in cached data
                    for (var cp in $scope.cached_plots) {
                        if ($scope.cached_plots.hasOwnProperty(cp)) {
                            $scope.cached_plots[cp].cluster_data.forEach(function (cluster) {
                                if (cluster.cluster == sample_cluster.cluster) {
                                    cluster.labels = labels;
                                }
                            });
                        }
                    }
                }, function (error) {
                    sample_cluster.label_error = "Updating cluster labels failed!";
                });
            }

            $scope.add_cluster_label = function (label, sample_cluster) {
                sample_cluster.label_error = null;
                var response = ModelService.createClusterLabel(
                    {
                        'cluster': sample_cluster.cluster, // the cluster ID
                        'label': label.id
                    }
                );

                response.$promise.then(function (object) {
                    // success, update the sample cluster's cluster labels
                    update_cluster_labels(sample_cluster);
                }, function (error) {
                    sample_cluster.label_error = "Saving label failed!";
                });

            };

            $scope.remove_cluster_label = function (label, sample_cluster) {
                sample_cluster.label_error = null;

                var response = ModelService.destroyClusterLabel(
                    label
                );

                response.$promise.then(function (object) {
                    // success, update the sample cluster's cluster labels
                    update_cluster_labels(sample_cluster);
                }, function (error) {
                    sample_cluster.label_error = "Deleting label failed!";
                });

            };

            $scope.toggle_animation = function () {
                if ($scope.animate) {
                    $scope.transition_ms = 1000;
                } else {
                    $scope.transition_ms = 0;
                }
            };

            $scope.set_cluster_display = function () {
                // Shows/hides cluster circles using visibility property,
                // not opacity. Visibility lets us control mouse-events and
                // is computationally less intense
                if ($scope.cluster_display_mode === "all") {
                    $scope.clusters.attr("visibility", "visible");
                } else if ($scope.cluster_display_mode === "none")  {
                    $scope.clusters.attr("visibility", "hidden");
                } else {
                    // the only mode left is "expanded", and for that we need to
                    // iterate over the clusters to see their "display_events"
                    // property
                    $scope.clusters.filter(function(d, i) {
                        if (d.display_events) {
                            return d;
                        }
                    }).attr("visibility", "visible");
                    $scope.clusters.filter(function(d, i) {
                        if (!d.display_events) {
                            return d;
                        }
                    }).attr("visibility", "hidden");
                }
            };

            $scope.set_cluster_radius = function () {
                // Controls size of cluster radii, either proportional
                // to event percentage or fixed at 6 pixels
                $scope.clusters.attr("r", function (d) {
                    if ($scope.static_cluster_size) {
                        return 6;
                    } else {
                        return Math.round(d.event_percentage) + 6;
                    }
                });
            };

            $scope.process_cluster_events = function (cluster) {
                // first retrieve SampleCluster CSV
                var response = ModelService.getSampleClusterCSV(cluster.id);

                response.then(function (event_csv) {
                    // success
                    cluster.events = d3.csv.parse(event_csv.data);
                    cluster.events_retrieved = true;

                    $scope.render_plot();
                }, function (error) {
                    console.log("Error retrieving sample cluster events")
                });
            };

            $scope.launch_stage2_modal = function() {
                var stage2_params = [];
                $scope.plot_data.panel_data.parameters.forEach(function (p) {
                    if (p.parameter_type != 'TIM' && p.parameter_type != 'NUL') {
                        stage2_params.push(p);
                    }
                });
                // launch form modal
                $modal.open({
                    templateUrl: MODAL_URLS.PR_STAGE2,
                    controller: 'ModalFormCtrl',
                    size: 'lg',
                    resolve: {
                        instance: function() {
                            return {
                                'parent_pr_id': $scope.$parent.process_request.id,
                                'cell_subsets': $scope.labels,
                                'parameters': stage2_params,
                                'clusters': $scope.plot_data.cluster_data
                            };
                        }
                    }
                });
            };

            $scope.launch_multi_label_modal = function() {
                // launch form modal
                $modal.open({
                    templateUrl: MODAL_URLS.PR_MULTI_LABEL,
                    controller: 'ModalFormCtrl',
                    resolve: {
                        instance: function() {
                            return {
                                'add_cluster_label': $scope.add_cluster_label,
                                'parent_pr_id': $scope.$parent.process_request.id,
                                'cell_subsets': $scope.labels,
                                'clusters': $scope.plot_data.cluster_data
                            };
                        }
                    }
                });
            };

            $scope.launch_single_label_modal = function(sample_cluster) {
                // launch form modal
                $modal.open({
                    templateUrl: MODAL_URLS.PR_SINGLE_LABEL,
                    controller: 'ModalFormCtrl',
                    resolve: {
                        instance: function() {
                            return {
                                'add_cluster_label': $scope.add_cluster_label,
                                'parent_pr_id': $scope.$parent.process_request.id,
                                'cell_subsets': $scope.labels,
                                'cluster': sample_cluster
                            };
                        }
                    }
                });
            };
        }
    ]
);

app.directive('prscatterplot', function() {
    function link(scope) {
        var width = 560;         // width of the svg element
        var height = 520;         // height of the svg element
        scope.canvas_width = 480;   // width of the canvas
        scope.canvas_height = 480;  // height of the canvas
        var colors = d3.scale.category20().range();
        var margin = {          // used mainly for positioning the axes' labels
            top: 0,
            right: 0,
            bottom: height - scope.canvas_height,
            left: width - scope.canvas_width
        };
        scope.cluster_radius = 8;
        scope.cluster_radius_lg = 10;
        scope.transition_ms = 1000;
        scope.heat_base_color = "#5888D0";
        scope.parameters = [];  // flow data column names
        scope.show_heat = false;    // whether to show heat map
        scope.static_cluster_size = false;  // fixed size cluster radii
        scope.auto_scale = true;  // automatically scales axes to data
        scope.auto_transition = true;  // transition param changes immediately
        scope.animate = true;  // controls whether transitions animate
        scope.enable_brushing = false;  // toggles selection by brushing mode
        scope.parameter_changed_flag = false;  // detect if x or y changed

        // controls display of cluster centers, there are 3 modes:
        //  - "all" (default)
        //  - "expanded"
        //  - "none"
        scope.cluster_display_mode = "all";

        // Transition variables
        scope.prev_position = [];         // prev_position [x, y, color] pairs
        scope.transition_count = 100;       // used to cancel old transitions

        var tmp_param = [];  // for building parameter 'full_name'
        var tmp_markers = [];  // also for param 'full_name' to sort markers

        // A tooltip for displaying the point's event values
        var tooltip = d3.select("body")
            .append("div")
            .attr("id", "tooltip")
            .style("position", "absolute")
            .style("z-index", "100")
            .style("visibility", "hidden");


        scope.svg = d3.select("#scatterplot")
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("style", "z-index: 1000");

        var plot_area = scope.svg.append("g")
            .attr("id", "plot-area");

        scope.cluster_plot_area = plot_area.append("g")
            .attr("id", "cluster-plot-area")
            .attr("transform", "translate(" + margin.left + ", " + 0 + ")");

        scope.brush = d3.svg.brush()
            .on("brush", brushed);

        function brushed() {
            var e = scope.brush.extent();

            // Breaking down the extent for easier reading :)
            var x_min = e[0][0];
            var x_max = e[1][0];
            var y_min = e[0][1];
            var y_max = e[1][1];

            // Highlight selected circles
            scope.svg.selectAll("circle").filter(function(d) {
                return d3.select(this).attr("visibility") === "visible";
            }).classed("selected", function(d) {
                var x_location = null;
                var y_location = null;

                d.parameters.forEach(function (p) {
                    if (p.channel == scope.x_param.fcs_number) {
                        x_location = p.location;
                    }
                    if (p.channel == scope.y_param.fcs_number) {
                        y_location = p.location;
                    }
                });

                var is_selected = x_location > x_min && x_location < x_max
                    && y_location > y_min && y_location < y_max;

                if (is_selected) {
                    scope.select_cluster(d);
                } else {
                    scope.deselect_cluster(d);
                }

                return is_selected;
            });
        }

        scope.x_axis = plot_area.append("g")
            .attr("class", "axis")
            .attr("transform", "translate(" + margin.left + "," + scope.canvas_height + ")");

        scope.y_axis = plot_area.append("g")
            .attr("class", "axis")
            .attr("transform", "translate(" + margin.left + "," + 0 + ")");

        scope.x_label = scope.svg.append("text")
            .attr("class", "axis-label")
            .attr("transform", "translate(" + (scope.canvas_width / 2 + margin.left) + "," + (height - 3) + ")");

        scope.y_label = scope.svg.append("text")
            .attr("class", "axis-label")
            .attr("transform", "translate(" + margin.left / 4 + "," + (scope.canvas_height / 2) + ") rotate(-90)");

        scope.initialize_scatterplot = function(is_cached) {
            // clear any existing canvases
            d3.select('#scatterplot').selectAll('canvas').remove();

            // Add heat map canvas
            scope.heat_map_data = [];
            d3.select("#scatterplot")
                .append("canvas")
                .attr("id", "heat_map_canvas")
                .attr("style", "position:absolute;left: " + margin.left + "px; top: " + margin.top + "px;")
                .attr("width", scope.canvas_width)
                .attr("height", scope.canvas_height);

            var heat_map_canvas = document.getElementById("heat_map_canvas");
            scope.heat_map_ctx = heat_map_canvas.getContext('2d');

            scope.heat_map = heat.create(
                {
                    canvas: heat_map_canvas,
                    radius: 5
                }
            );

            scope.plot_data.cluster_data.forEach(function (cluster) {
                if (!is_cached) {
                    // set booleans for controlling the display of a
                    // cluster's events & for whether cluster is highlighted,
                    // selected, or expanded
                    // Note:
                    //   When display_events is true the cluster is
                    //   "expanded". If the cluster_display_mode is set to
                    //   "expanded" then only those cluster circles shall
                    //   be visible...this isn't controlled here directly but
                    //   is related to the display_events property.
                    cluster.display_events = false;
                    cluster.highlighted = false;
                    cluster.selected = false;
                    cluster.color = colors[cluster.cluster_index % 20];
                    cluster.pulse = false;

                    // and set an empty array for the cluster's event data
                    cluster.events = [];
                    // flag indicating cluster's events have been retrieved
                    cluster.events_retrieved = false;
                }

                // each cluster needs it's own canvas and canvas context
                d3.select("#scatterplot")
                    .append("canvas")
                    .attr("id", "cluster_" + cluster.cluster_index)
                    .attr("style", "position:absolute;left: " + margin.left + "px; top: " + margin.top + "px;")
                    .attr("width", scope.canvas_width)
                    .attr("height", scope.canvas_height);

                var canvas = document.getElementById("cluster_" + cluster.cluster_index);
                cluster.ctx = canvas.getContext('2d');
            });

            // reset the parameters, and build the friendly "full_name" for
            // each parameter to improve usability, otherwise users will not
            // be able to differentiate the parameters
            // TODO: Bad! this just creates a reference and alters panel_data
            // just iterate over panel_data.parameters directly
            scope.parameters = scope.plot_data.panel_data.parameters;
            scope.parameters.forEach(function(p) {
                tmp_param = [];
                tmp_markers = [];

                p.markers.forEach(function(m) {
                    tmp_markers.push(m.name);
                });
                tmp_markers.sort();

                tmp_param = tmp_param.concat(
                    [
                        p.parameter_type,
                        p.parameter_value_type
                    ],
                    tmp_markers
                );

                if (p.fluorochrome != null) {
                    tmp_param.push(
                        p.fluorochrome.fluorochrome_abbreviation
                    );
                }

                p.full_name = tmp_param.join(' ');

                // for submitting 2nd stage PRs
                p.full_name_underscored = tmp_param.join('_');
            });

            // reset the SVG clusters
            scope.clusters = null;
            scope.cluster_plot_area.selectAll("circle").remove();

            // if the user is switching between samples, the new sample
            // may have a matching parameter but it may be a different
            // channel (due to different site panels)
            scope.x_param = scope.find_matching_parameter(scope.x_param);
            if (scope.x_param == null) {
                scope.x_param = scope.analyzed_parameters[0];
            }
            scope.y_param = scope.find_matching_parameter(scope.y_param);
            if (scope.y_param == null) {
                scope.y_param = scope.analyzed_parameters[1];
            }

            scope.clusters = scope.cluster_plot_area.selectAll("circle").data(
                scope.plot_data.cluster_data
            );

            scope.clusters.enter()
                .append("circle")
                .attr("r", function (d) {
                        if (scope.static_cluster_size) {
                            return 6;
                        } else {
                            return Math.round(d.event_percentage) + 6;
                        }
                    }
                )
                .attr("fill", function (d) {
                    return d.color;
                })
                .style("stroke-width", function(d) {
                    if (d.display_events) {
                        return "4px";
                    } else {
                        return "1.2px";
                    }
                })
                .style("stroke-dasharray", function(d) {
                    if (d.display_events) {
                        return "4, 1";
                    } else {
                        return "1, 0";
                    }
                })
                .style("pointer-events", "visible")  // disable mouse events for hidden clusters
                .on("mouseenter", function(d) {
                    if (scope.cluster_display_mode === "none") {
                        return;
                    } else if (scope.cluster_display_mode === "expanded") {
                        if (!d.display_events) {
                            return;
                        }
                    }

                    tooltip.style("visibility", "visible")
                        .style("z-index", 9999);
                    tooltip.text("Cluster " + d.cluster_index + " (" + d.event_percentage + "%)");

                    scope.highlight_cluster(d);
                    scope.$apply();
                })
                .on("mousemove", function() {
                    return tooltip
                        .style(
                        "top",
                            (d3.event.pageY - 18) + "px")
                        .style(
                        "left",
                            (d3.event.pageX + 18) + "px"
                    );
                })
                .on("mouseout", function(d) {
                    scope.dehighlight_cluster(d);
                    scope.$apply();
                    return tooltip.style("visibility", "hidden");
                })
                .on("click", function(cluster) {
                    scope.toggle_cluster_events(cluster);
                    scope.$apply();
                });

            // sort circles by event percentage in descending order
            // to bring smaller clusters to the front
            // SVG elements don't obey z-index, they are in the order of
            // appearance
            scope.cluster_plot_area.selectAll("circle").sort(
                function (a, b) {
                    var a_event_percentage = parseFloat(a.event_percentage);
                    var b_event_percentage = parseFloat(b.event_percentage);
                    if (a_event_percentage > b_event_percentage) {
                        return -1;
                    } else if (a_event_percentage < b_event_percentage) {
                        return 1;
                    } else {
                        return 0;
                    }
                }
            );

            scope.render_plot();
        };
    }

    return {
        link: link,
        controller: 'PRScatterplotController',
        restrict: 'E',
        replace: true,
        templateUrl: 'static/ng-app/directives/pr_scatterplot.html'
    };
});

app.controller('PRScatterplotController', ['$scope', function ($scope) {
    var x_range;              // used for "auto-range" for chosen x category
    var y_range;              // used for "auto-range" for chosen y category
    var x_scale;              // function to convert x data to svg pixels
    var y_scale;              // function to convert y data to svg pixels

    // function to generate sample events in the canvas
    function render_event(ctx, pos) {
        ctx.strokeStyle = pos[2];
        ctx.globalAlpha = 1;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(pos[0], pos[1], 1.5, 0, 2 * Math.PI, false);
        ctx.stroke();
    }

    function toggle_cluster_events(cluster) {
        // this function separates the transitioning logic to
        // allow both toggling of a single cluster and toggling
        // all clusters without creating lots of transition loops
        cluster.display_events = !cluster.display_events;
        if (!cluster.events_retrieved) {
            // retrieve sample cluster events & process
            $scope.process_cluster_events(cluster);
        }

        // toggle cluster lines
        if (cluster.display_events) {
            $scope.select_cluster_line(cluster);
            $scope.expand_cluster(cluster);
        } else {
            $scope.deselect_cluster_line(cluster);
            $scope.collapse_cluster(cluster);
        }
    }

    $scope.toggle_all_events = function () {
        $scope.show_all_clusters = !$scope.show_all_clusters;

        $scope.plot_data.cluster_data.forEach(function(c) {
            c.display_events = !$scope.show_all_clusters;
            toggle_cluster_events(c);
        });

        // Now transition everything
        $scope.render_plot();
    };

    $scope.toggle_cluster_events = function (cluster) {
        toggle_cluster_events(cluster);

        // Now, transition the events if we have them
        if (cluster.events_retrieved) {
            $scope.render_plot();
        }
    };

    $scope.expand_selected_clusters = function () {
        // Make a list of the selected clusters since things may move
        // with the toggle_cluster_events call and cause other clusters to
        // move into the selection before the transitions are complete
        var clusters_to_expand = [];
        $scope.plot_data.cluster_data.forEach(function(c) {
            if (c.selected && !c.display_events) {
                // call $scope.toggle...here because events may not be retrieved
                clusters_to_expand.push(c);
            }
        });

        clusters_to_expand.forEach(function(c){
            $scope.toggle_cluster_events(c);
        });

        // clear brush region
        $scope.brush.clear();
        $scope.svg.selectAll(".brush").call($scope.brush);

        $scope.render_plot();
    };

    $scope.collapse_selected_clusters = function () {
        $scope.plot_data.cluster_data.forEach(function(c) {
            if (c.selected && c.display_events) {
                // don't call $scope.toggle...we don't want to trigger renders
                // as we'll do it ourselves afterwards
                toggle_cluster_events(c);
            }
        });

        // clear brush region
        $scope.brush.clear();
        $scope.svg.selectAll(".brush").call($scope.brush);

        $scope.parameter_changed_flag = true;  // trigger deselection in render
        $scope.render_plot();
    };

    $scope.set_brushing_mode = function() {
        // If brushing is enabled, update the brush scale
        // & re-append our updated brush to the plot, then finally
        // issue brush.call
        if ($scope.enable_brushing) {
            $scope.brush
                .x(x_scale)
                .y(y_scale);
            $scope.cluster_plot_area.append("g")
                .attr("class", "brush")
                .call($scope.brush);
            $scope.brush.event(d3.select("g.brush"));
        } else {
            // Clear any existing brushes if brush mode is off
            $scope.svg.selectAll(".brush").call($scope.brush.clear());

            // Remove brush from the SVG
            d3.selectAll("g.brush").remove();

            // turn off "selected" status on any previously selected clusters
            // else they can get stuck as selected if the user disables the
            // brushed mode
            $scope.plot_data.cluster_data.forEach(function(c) {
                if (c.selected) {
                    $scope.deselect_cluster(c);
                }
            });
        }
    };

    $scope.render_plot = function () {
        // Update the axes' labels with the new categories
        $scope.x_label.text($scope.x_param.full_name);
        $scope.y_label.text($scope.y_param.full_name);

        // for determining min/max values for x & y auto-scaling
        var x_cluster_location;  
        var y_cluster_location;
        var tmp_x_extent;
        var tmp_y_extent;
        var x_extent = undefined;  // no default starting extents
        var y_extent = undefined;

        // set cluster circle visibility
        $scope.set_cluster_display();

        // For auto-scaling, get cluster locations & any displayed event data
        // for chosen x & y parameters to determine axis extents.
        // If auto-scaling is off, use the user-provided values
        x_range = [];
        y_range = [];
        if ($scope.auto_scale) {
            for (var i=0, len=$scope.plot_data.cluster_data.length; i<len; i++) {
                // get the x, y locations for this cluster...this will exist
                // for all clusters
                $scope.plot_data.cluster_data[i].parameters.forEach(function (p) {
                    if (p.channel == $scope.x_param.fcs_number) {
                        x_cluster_location = p.location;
                    }
                    if (p.channel == $scope.y_param.fcs_number) {
                        y_cluster_location = p.location;
                    }
                });

                // x & y extents start out undefined, so set them the first go
                // round using the guaranteed cluster data from the 1st cluster
                if (x_extent === undefined) {
                    x_extent = [x_cluster_location, x_cluster_location];
                    y_extent = [y_cluster_location, y_cluster_location];
                } else {
                    // compare against current cluster location
                    if (x_cluster_location < x_extent[0]) {
                        x_extent[0] = x_cluster_location;
                    }
                    if (x_cluster_location > x_extent[1]) {
                        x_extent[1] = x_cluster_location;
                    }

                    if (y_cluster_location < y_extent[0]) {
                        y_extent[0] = y_cluster_location;
                    }
                    if (y_cluster_location > y_extent[1]) {
                        y_extent[1] = y_cluster_location;
                    }
                }

                // consider event data for clusters w/ displayed events,
                // however even if the cluster is set to display events, it
                // still may have zero events to display, so we have to deal
                // with possible undefined values returned from d3.extent
                if ($scope.plot_data.cluster_data[i].display_events) {
                    tmp_x_extent = d3.extent(
                        $scope.plot_data.cluster_data[i].events,
                        function (e_obj) {
                            return parseFloat(e_obj[$scope.x_param.fcs_number]);
                        }
                    );
                    tmp_y_extent = d3.extent(
                        $scope.plot_data.cluster_data[i].events,
                        function (e_obj) {
                            return parseFloat(e_obj[$scope.y_param.fcs_number]);
                        }
                    );

                    // there may be zero events in the cluster, and we don't
                    // need to check both x & y, if x is undefined, so is y
                    if (tmp_x_extent.indexOf(undefined) === -1) {
                        // we've got event data, so compare
                        // current extent vs event data
                        if (tmp_x_extent[0] < x_extent[0]) {
                            x_extent[0] = tmp_x_extent[0];
                        }
                        if (tmp_x_extent[1] > x_extent[1]) {
                            x_extent[1] = tmp_x_extent[1];
                        }

                        if (tmp_y_extent[0] < y_extent[0]) {
                            y_extent[0] = tmp_y_extent[0];
                        }
                        if (tmp_y_extent[1] > y_extent[1]) {
                            y_extent[1] = tmp_y_extent[1];
                        }
                    }
                }
            }

            // Add some padding as well to keep objects from the sides
            x_range = [
                x_extent[0] - (0.05 * (x_extent[1] - x_extent[0])),
                x_extent[1] + (0.05 * (x_extent[1] - x_extent[0]))
            ];
            y_range = [
                y_extent[0] - (0.05 * (y_extent[1] - y_extent[0])),
                y_extent[1] + (0.05 * (y_extent[1] - y_extent[0]))
            ];

            // Set text box values
            $scope.user_x_min = x_range[0].toFixed(2);
            $scope.user_x_max = x_range[1].toFixed(2);
            $scope.user_y_min = y_range[0].toFixed(2);
            $scope.user_y_max = y_range[1].toFixed(2);
        } else {
            x_range.push($scope.user_x_min);
            x_range.push($scope.user_x_max);
            y_range.push($scope.user_y_min);
            y_range.push($scope.user_y_max);
        }

        // Update scaling functions for determining placement of the x and y axes
        x_scale = d3.scale.linear().domain(x_range).range([0, $scope.canvas_width]);
        y_scale = d3.scale.linear().domain(y_range).range([$scope.canvas_height, 0]);

        // Update axes with the proper scaling, but we'll determine tick format
        // based on ranges first
        var x_tick_format;
        var y_tick_format;
        if (x_range[1] >= 1000) {
            x_tick_format = "s";
        } else {
            x_tick_format = "g";
        }
        if (y_range[1] >= 1000) {
            y_tick_format = "s";
        } else {
            y_tick_format = "g";
        }
        $scope.x_axis.call(d3.svg.axis()
            .scale(x_scale)
            .tickFormat(d3.format(x_tick_format))
            .orient("bottom")
        );
        $scope.y_axis.call(d3.svg.axis()
            .scale(y_scale)
            .tickFormat(d3.format(y_tick_format))
            .orient("left")
        );

        // transition SVG clusters
        $scope.clusters.transition().duration($scope.transition_ms)
            .attr("cx", function (d) {
                for (var i=0; i < d.parameters.length; i++) {
                    if (d.parameters[i].channel == $scope.x_param.fcs_number) {
                        return x_scale(d.parameters[i].location);
                    }
                }
            })
            .attr("cy", function (d) {
                for (var i=0; i < d.parameters.length; i++) {
                    if (d.parameters[i].channel == $scope.y_param.fcs_number) {
                        return y_scale(d.parameters[i].location);
                    }
                }
            });

        // If brushing is enabled, update the brush scale as the scale may
        // have changed and some clusters may have moved out of the brush
        if ($scope.enable_brushing) {
            $scope.brush
                .x(x_scale)
                .y(y_scale);
            $scope.brush.event(d3.select("g.brush"));

            // however, if the parameter had changed we want to clear any
            // brush, since the old brush location doesn't really make
            // sense in the new parameter
            if ($scope.parameter_changed_flag) {
                $scope.svg.selectAll(".brush").call($scope.brush.clear());
                $scope.parameter_changed_flag = false;

                // turn off "selected" status on any previously selected clusters
                // else they can get stuck as selected
                $scope.plot_data.cluster_data.forEach(function(c) {
                    if (c.selected) {
                        $scope.deselect_cluster(c);
                    }
                });
            }
        }

        $scope.transition_canvas_events(++$scope.transition_count);
    };

    $scope.transition_canvas_events = function (count) {
        // Clear heat map canvas before the transitions
        $scope.heat_map_ctx.clearRect(
            0, 0, $scope.heat_map_ctx.canvas.width, $scope.heat_map_ctx.canvas.height);
        $scope.heat_map_data = [];

        // iterate through clusters that are marked for display
        $scope.plot_data.cluster_data.forEach(function (cluster) {
            if (cluster.display_events) {
                cluster.next_position = [];

                // iterate through all cluster events to set its next position
                cluster.events.forEach(function (event) {
                    cluster.next_position.push(
                        [
                            x_scale(event[$scope.x_param.fcs_number]),
                            y_scale(event[$scope.y_param.fcs_number]),
                            $scope.show_heat ? $scope.heat_base_color : cluster.color
                        ]
                    );
                });

                if (!cluster.prev_position) {
                    cluster.prev_position = cluster.next_position;
                }

                // set cluster's interpolator
                cluster.interpolator = d3.interpolate(
                    cluster.prev_position,
                    cluster.next_position
                );

                // run transition
                d3.timer(function (t) {
                    // Clear canvas
                    // Use the identity matrix while clearing the canvas
                    cluster.ctx.clearRect(
                        0,
                        0,
                        cluster.ctx.canvas.width,
                        cluster.ctx.canvas.height
                    );

                    // abort old transition
                    if (count < $scope.transition_count) return true;

                    // transition for time t, in milliseconds
                    if (t > $scope.transition_ms) {
                        cluster.prev_position = cluster.next_position;
                        cluster.prev_position.forEach(function (position) {
                            render_event(cluster.ctx, position);
                        });

                        if ($scope.show_heat) {
                            $scope.heat_map_ctx.clearRect(
                                0,
                                0,
                                $scope.heat_map_ctx.canvas.width,
                                $scope.heat_map_ctx.canvas.height
                            );

                            cluster.prev_position.forEach(function (pos) {
                                $scope.heat_map_data.push({x: pos[0], y: pos[1]});
                            });

                            $scope.heat_map.set_data($scope.heat_map_data);
                            $scope.heat_map.colorize();
                        }

                        return true
                    }

                    cluster.prev_position = cluster.interpolator(t / $scope.transition_ms);
                    cluster.prev_position.forEach(function (position) {
                        render_event(cluster.ctx, position);
                    });

                    return false;
                });
            } else {
                // This cluster's display is off.
                // Clear canvas
                // Use the identity matrix while clearing the canvas
                cluster.ctx.clearRect(
                    0,
                    0,
                    cluster.ctx.canvas.width,
                    cluster.ctx.canvas.height
                );
            }
        });
    }
}]);