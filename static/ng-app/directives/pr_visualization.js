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
        $scope.sample_collection = data;
        $scope.cached_plots = {};
    });

    $scope.initialize_visualization = function() {
        // TODO: turning off cached_plots checking b/c the cluster
        // labels need to be updated, need to create a different mechanism
        // to update only the labels

        //if ($scope.chosen_member.id in $scope.cached_plots) {
        //    $scope.plot_data = $scope.cached_plots[$scope.chosen_member.id];
        //    $scope.initialize_scatterplot();
        //    $scope.initialize_parallel_plot();
        //    return;
        //}

        $scope.retrieving_data = true;
        sample_clusters = ModelService.getSampleClusters(
            $scope.$parent.process_request.id,
            $scope.chosen_member.sample.id
        );

        panel_data = ModelService.getSitePanel(
            $scope.chosen_member.sample.site_panel
        );

        $q.all([sample_clusters, panel_data]).then(function(data) {
            $scope.cached_plots[$scope.chosen_member.id] = {
                'cluster_data': data[0],
                'panel_data': data[1]
            };
            $scope.plot_data = $scope.cached_plots[$scope.chosen_member.id];
            $scope.initialize_scatterplot();
            $scope.initialize_parallel_plot();
        }).catch(function(e) {
            // show errors here
            console.log('error!')
        }).finally(function() {
            $scope.retrieving_data = false;
        });
    };

    $scope.find_matching_parameter = function (param) {
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

    $scope.select_cluster = function (cluster) {
        cluster.selected = true;

        $scope.clusters.filter(
            function(d) {
                if (d.cluster_index == cluster.cluster_index) {
                    return d;
                }
            }).attr("r", 12);

        $scope.select_cluster_line(cluster);
    };

    $scope.deselect_cluster = function (cluster) {
        cluster.selected = false;

        $scope.clusters.filter(
            function(d) {
                if (d.cluster_index == cluster.cluster_index) {
                    return d;
                }
            }).attr("r", 8);

        $scope.deselect_cluster_line(cluster);
    };

    $scope.add_cluster_label = function (label, sample_cluster) {
        sample_cluster.label_error = null;
        var response = ModelService.createClusterLabel(
            {
                'cluster': sample_cluster.cluster, // the cluster ID
                'label': label.id
            }
        );

        response.$promise.then(function (object) {
            // success, nothing to do
        }, function (error) {
            sample_cluster.label_error = "Saving label failed!";
        });

    };

    $scope.remove_cluster_label = function (label, sample_cluster) {
        sample_cluster.label_error = null;

        // first, need to retrieve the PK for our ClusterLabel, as
        // the sample_cluster.labels stores the CellSubsetLabel PK
        // So, we do a query and expect only one result, a faux-GET
        var cluster_labels = ModelService.getClusterLabels(
            {
                'cluster': sample_cluster.cluster,
                'label': label.id
            }
        );

        cluster_labels.$promise.then(function (object) {
            var response = ModelService.destroyClusterLabel(
                object[0]
            );

            response.$promise.then(function (object) {
                // success, nothing to do
            }, function (error) {
                sample_cluster.label_error = "Deleting label failed!";
            });
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

    $scope.toggle_clusters = function () {
        if ($scope.show_clusters) {
            $scope.clusters.style("opacity", 1);
        } else {
            $scope.clusters.style("opacity", 0);
        }
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

        });
    };

    $scope.launch_stage2_modal = function() {

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
                        'parameters': $scope.plot_data.panel_data.parameters,
                        'clusters': $scope.plot_data.cluster_data
                    };
                }
            }
        });
    };
}]);

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
        var cluster_radius = 8;
        scope.transition_ms = 1000;
        scope.heat_base_color = "#5888D0";
        scope.parameters = [];  // flow data column names
        scope.show_heat = false;    // whether to show heat map
        scope.auto_scale = true;  // automatically scales axes to data
        scope.animate = true;  // controls whether transitions animate
        scope.show_clusters = true;  // controls display of cluster centers

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

        var cluster_plot_area = plot_area.append("g")
            .attr("id", "cluster-plot-area")
            .attr("transform", "translate(" + margin.left + ", " + 0 + ")");

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

        scope.initialize_scatterplot = function() {
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
                // set booleans for controlling the display of a
                // cluster's events & for whether cluster is selected
                cluster.display_events = false;
                cluster.selected = false;
                cluster.color = colors[cluster.cluster_index % 20];

                // and set an empty array for the cluster's event data
                cluster.events = [];
                // flag indicating cluster's events have been retrieved
                cluster.events_retrieved = false;

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
            cluster_plot_area.selectAll("circle").remove();

            // if the user is switching between samples, the new sample
            // may have a matching parameter but it may be a different
            // channel (due to different site panels)
            scope.x_param = scope.find_matching_parameter(scope.x_param);
            if (scope.x_param == null) {
                scope.x_param = scope.parameters[0];
            }
            scope.y_param = scope.find_matching_parameter(scope.y_param);
            if (scope.y_param == null) {
                scope.y_param = scope.parameters[0];
            }

            scope.clusters = cluster_plot_area.selectAll("circle").data(
                scope.plot_data.cluster_data
            );

            scope.clusters.enter()
                .append("circle")
                .attr("r", cluster_radius)
                .attr("fill", function (d) {
                    return d.color;
                })
                .on("mouseenter", function(d) {
                    if (!scope.show_clusters) {
                        return;
                    }

                    tooltip.style("visibility", "visible");
                    tooltip.text("Cluster " + d.cluster_index + " (" + d.weight + "%)");

                    scope.select_cluster(d);
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
                    scope.deselect_cluster(d);
                    scope.$apply();
                    return tooltip.style("visibility", "hidden");
                })
                .on("click", function(cluster, index) {
                    scope.toggle_cluster_events(cluster);
                    scope.$apply();
                });

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
    var x_data;               // x data series to plot
    var y_data;               // y data series to plot
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
        } else {
            $scope.deselect_cluster_line(cluster);
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

    $scope.render_plot = function () {
        // Update the axes' labels with the new categories
        $scope.x_label.text($scope.x_param.full_name);
        $scope.y_label.text($scope.y_param.full_name);

        // holds the x & y locations for the clusters
        x_data = [];
        y_data = [];

        // for determining min/max values for x & y
        var tmp_x_extent;
        var tmp_y_extent;
        $scope.x_param.extent = undefined;
        $scope.y_param.extent = undefined;

        // Populate x_data and y_data using chosen x & y parameters
        for (var i=0, len=$scope.plot_data.cluster_data.length; i<len; i++) {
            $scope.plot_data.cluster_data[i].parameters.forEach(function (p) {
                if (p.channel == $scope.x_param.fcs_number) {
                    x_data[i] = p.location;
                }
                if (p.channel == $scope.y_param.fcs_number) {
                    y_data[i] = p.location;
                }
            });

            // if auto-scaling, parse displayed events for extent
            if ($scope.auto_scale && $scope.plot_data.cluster_data[i].display_events) {
                tmp_x_extent = d3.extent(
                    $scope.plot_data.cluster_data[i].events,
                    function(e_obj) {
                        return parseFloat(e_obj[$scope.x_param.fcs_number]);
                    }
                );
                if ($scope.x_param.extent === undefined) {
                    $scope.x_param.extent = tmp_x_extent;
                } else {
                    if (tmp_x_extent[0] < $scope.x_param.extent[0]) {
                        $scope.x_param.extent[0] = tmp_x_extent[0];
                    }
                    if (tmp_x_extent[1] > $scope.x_param.extent[1]) {
                        $scope.x_param.extent[1] = tmp_x_extent[1];
                    }
                }

                tmp_y_extent = d3.extent(
                    $scope.plot_data.cluster_data[i].events,
                    function(e_obj) {
                        return parseFloat(e_obj[$scope.y_param.fcs_number]);
                    }
                );
                if ($scope.y_param.extent === undefined) {
                    $scope.y_param.extent = tmp_y_extent;
                } else {
                    if (tmp_y_extent[0] < $scope.y_param.extent[0]) {
                        $scope.y_param.extent[0] = tmp_y_extent[0];
                    }
                    if (tmp_y_extent[1] > $scope.y_param.extent[1]) {
                        $scope.y_param.extent[1] = tmp_y_extent[1];
                    }
                }
            }
        }

        // check for auto-scaling
        x_range = [];
        y_range = [];
        if ($scope.auto_scale) {
            // find the true extent of the combined cluster locations and
            // the displayed events.
            if ($scope.x_param.extent !== undefined) {
                if (x_data.length > 0) {
                    x_range = [
                        math.min(math.min(x_data), $scope.x_param.extent[0]),
                        math.max(math.max(x_data), $scope.x_param.extent[1])
                    ];
                } else {
                    x_range = $scope.x_param.extent;
                }
            } else {
                if (x_data.length > 0) {
                    x_range = [
                        math.min(x_data),
                        math.max(x_data)
                    ];
                }
            }

            if ($scope.y_param.extent !== undefined) {
                if (y_data.length > 0) {
                    y_range = [
                        math.min(math.min(y_data), $scope.y_param.extent[0]),
                        math.max(math.max(y_data), $scope.y_param.extent[1])
                    ];
                } else {
                    y_range = $scope.y_param.extent;
                }
            } else {
                if (y_data.length > 0) {
                    y_range = [
                        math.min(y_data),
                        math.max(y_data)
                    ];
                }
            }

            // Add some padding as well to keep objects from the sides
            x_range = [
                x_range[0] - (0.05 * (x_range[1] - x_range[0])),
                x_range[1] + (0.05 * (x_range[1] - x_range[0]))
            ];
            y_range = [
                y_range[0] - (0.05 * (y_range[1] - y_range[0])),
                y_range[1] + (0.05 * (y_range[1] - y_range[0]))
            ];

            // Set text box values
            $scope.user_x_min = x_range[0];
            $scope.user_x_max = x_range[1];
            $scope.user_y_min = y_range[0];
            $scope.user_y_max = y_range[1];
        } else {
            x_range.push($scope.user_x_min);
            x_range.push($scope.user_x_max);
            y_range.push($scope.user_y_min);
            y_range.push($scope.user_y_max);
        }

        // Update scaling functions for determining placement of the x and y axes
        x_scale = d3.scale.linear().domain(x_range).range([0, $scope.canvas_width]);
        y_scale = d3.scale.linear().domain(y_range).range([$scope.canvas_height, 0]);

        // Update axes with the proper scaling
        $scope.x_axis.call(d3.svg.axis().scale(x_scale).orient("bottom"));
        $scope.y_axis.call(d3.svg.axis().scale(y_scale).orient("left"));

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