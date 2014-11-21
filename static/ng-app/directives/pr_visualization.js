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
        'ModelService',
        function ($scope, $q, ModelService) {
    var sample_clusters = null;
    var panel_data = null;
    var event_data = null;

    $scope.$watch('data', function(data) {
        $scope.sample_collection = data;
        $scope.cached_plots = {};
    });

    $scope.initialize_visualization = function() {
        if ($scope.chosen_member.id in $scope.cached_plots) {
            $scope.plot_data = $scope.cached_plots[$scope.chosen_member.id];
            $scope.initialize_scatterplot();
            $scope.initialize_parallel_plot();
            return;
        }

        $scope.retrieving_data = true;
        sample_clusters = ModelService.getSampleClusters(
            $scope.$parent.process_request.id,
            $scope.chosen_member.sample.id
        );

        panel_data = ModelService.getSitePanel(
            $scope.chosen_member.sample.site_panel
        );

        event_data = ModelService.getSampleCSV(
            $scope.chosen_member.sample.id
        );

        $q.all([sample_clusters, panel_data, event_data]).then(function(data) {
            $scope.cached_plots[$scope.chosen_member.id] = {
                'cluster_data': data[0],
                'panel_data': data[1],
                'event_data': data[2].data,
                'compensation_data': $scope.chosen_member.compensation
            };
            $scope.plot_data = $scope.cached_plots[$scope.chosen_member.id];
            $scope.initialize_scatterplot();
            $scope.initialize_parallel_plot();
        }).catch(function() {
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

    function parse_compensation(comp_csv) {
        // comp_csv is a text string to convert to a comp matrix object
        // with 2 properties:
        //     "indices": a list of indices to transform
        //     "matrix": the compe matrix as a MathJS Matrix
        var lines = [];
        var header;

        comp_csv.split("\n").forEach(function (line) {
            if (line === "") {
                return;
            }
            lines.push(line.split(","));
        });

        header = lines.shift();
        for (var i=0; i < header.length; i++) {
            header[i] = parseInt(header[i]) - 1;  // we want indices
        }

        lines.forEach(function(l) {
            for (var i=0; i < l.length; i++) {
                l[i] = parseFloat(l[i]);
            }
        });

        lines = math.matrix(lines);

        return {
            "indices": header,
            "matrix": lines
        };
    }

    function compensate(event_object) {
        var event_subset = [];
        $scope.compensation.indices.forEach(function(i) {
            // event object values are strings, we need floats for MathJS
            event_subset.push(parseFloat(event_object[i]));
        });

        event_subset = math.multiply(
            event_subset,
            math.inv($scope.compensation.matrix)
        ).toArray();  // and back to array

        // and now convert back to strings
        $scope.compensation.indices.forEach(function(i) {
            event_object[i] = event_subset.shift().toString();
        });
    }

    function asinh(number) {
        return Math.log(number + Math.sqrt(number * number + 1));
    }

    $scope.select_cluster = function (cluster) {
        $scope.hover_cluster = cluster;

        // find x_param value
        cluster.parameters.forEach(function (p) {
            if (p.channel == $scope.x_param.fcs_number) {
                $scope.hover_x = (Math.round(p.location * 100) / 100).toString();
            }
        });
        // find y_param value
        cluster.parameters.forEach(function (p) {
            if (p.channel == $scope.y_param.fcs_number) {
                $scope.hover_y = (Math.round(p.location * 100) / 100).toString();
            }
        });

        cluster.selected = true;

        $scope.clusters.filter(
            function(d) {
                if (d.cluster_index == cluster.cluster_index) {
                    return d;
                }
            }).attr("r", 12);

        // highlight line in parallel chart
        $scope.parallel_lines.select("#cluster_" + cluster.cluster_index)
            .attr("class", "selected");

        // and now sort parallel chart lines by selection to bring it to the front
        // SVG elements don't obey z-index, they are in the order of
        // appearance
        $scope.parallel_lines.selectAll("path").sort(
            function (a, b) {
                return a.selected - b.selected;
            }
        );
    };

    $scope.deselect_cluster = function (cluster) {
        cluster.selected = false;

        $scope.clusters.filter(
            function(d) {
                if (d.cluster_index == cluster.cluster_index) {
                    return d;
                }
            }).attr("r", 8);

        // remove highlight in parallel chart
        $scope.parallel_lines.select("#cluster_" + cluster.cluster_index)
            .attr("class", "");
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

    $scope.process_event_data = function (event_csv) {
        // The sample's CSV file doesn't contain a header row, we'll create
        // one so the d3.csv.parse can conveniently make our objects for us.
        var n_columns = 0;
        var header = "event_index";
        for (var i=0; i < event_csv.length; i++) {
            if (event_csv[i] === ',') {
                n_columns++;
            } else if (event_csv[i] === '\n') {
                break;
            }
        }
        for (i=0; i < n_columns; i++) {
            header += "," + i.toString();
        }

        event_csv = header + "\n" + event_csv;

        // convert the compensation text to a MathJS Matrix
        $scope.compensation = parse_compensation($scope.plot_data.compensation_data);

        // compensate & transform the event data,
        // but not for scatter and time channels
        var event_objects = d3.csv.parse(event_csv, function(d) {
            // Always apply compensation first
            compensate(d);

            for (var prop in d) {
                if (d.hasOwnProperty(prop) && prop !== 'event_index') {
                    // check if this is a transform channel
                    if ($scope.transform_indices.indexOf(prop) != -1) {
                        // transform with pre-scaling factor
                        d[prop] = asinh(parseFloat(d[prop]) / 100);
                    }
                }
            }
            return d;
        });

        // get extent for all channels for auto-ranging the axis
        $scope.parameters.forEach(function(p) {
            p.extent = d3.extent(event_objects, function(eo) {
                return parseFloat(eo[p.fcs_number - 1]);
            });

            // pad ranges a bit, keeps the data points from
            // overlapping the plot's edge, and round up to next integer
            // for prettier user inputs for non-autoscaling
            p.extent[0] = (p.extent[0] - (p.extent[1] - p.extent[0]) * 0.02).toFixed(2);
            p.extent[1] = (p.extent[1] + (p.extent[1] - p.extent[0]) * 0.02).toFixed(2);
        });

        event_objects.forEach(function (e) {
            for (var i = 0; i < $scope.plot_data.cluster_data.length; i++) {
                if ($scope.plot_data.cluster_data[i].event_indices.indexOf(e.event_index) !== -1) {
                    $scope.plot_data.cluster_data[i].events.push(e);
                    break;
                }
            }
        });

        // populate cluster event percentage
        $scope.plot_data.cluster_data.forEach(function (c) {
            c.event_percent = (c.events.length / event_objects.length) * 100;
            c.event_percent = c.event_percent.toFixed(2);
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
        var margin = {            // used mainly for positioning the axes' labels
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
        scope.transform_indices = [];  // data column indices to transform
        var non_transform_param_types = [
            'FSC',
            'SSC',
            'TIM',
            'NUL'
        ];

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
            // Also, set the channels to transform. Scatter, time, and null
            // channels do not get transformed
            scope.parameters = scope.plot_data.panel_data.parameters;
            scope.transform_indices = [];
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

                // Now test if this is a channel we need to transform
                if (non_transform_param_types.indexOf(p.parameter_type) == -1) {
                    // data is zero-indexed
                    scope.transform_indices.push((p.fcs_number - 1).toString());
                }

            });

            // Now, convert the event_data CSV string into usable objects
            // and store each cluster's events in the cluster.events array
            scope.process_event_data(scope.plot_data.event_data);

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

            scope.x_pre_scale = '0.01';
            scope.y_pre_scale = '0.01';

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

                    scope.hover_cluster = d;

                    // find x_param value
                    d.parameters.forEach(function (p) {
                        if (p.channel == scope.x_param.fcs_number) {
                            scope.hover_x = (Math.round(p.location * 100) / 100).toString();
                        }
                    });
                    // find y_param value
                    d.parameters.forEach(function (p) {
                        if (p.channel == scope.y_param.fcs_number) {
                            scope.hover_y = (Math.round(p.location * 100) / 100).toString();
                        }
                    });

                    scope.select_cluster(d);
                    scope.$apply();
                })
                .on("mouseout", function(d) {
                    scope.deselect_cluster(d);
                    scope.$apply();
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
        var x_tmp, y_tmp;

        cluster.parameters.forEach(function (p) {
            if (p.channel == $scope.x_param.fcs_number) {
                x_tmp = x_scale(p.location);
            }
            if (p.channel == $scope.y_param.fcs_number) {
                y_tmp = y_scale(p.location);
            }
        });
    }

    $scope.toggle_all_events = function () {
        $scope.show_all_clusters = !$scope.show_all_clusters;

        $scope.plot_data.cluster_data.forEach(function(c) {
            c.display_events = !$scope.show_all_clusters;
            toggle_cluster_events(c);
        });

        // Now transition everything
        $scope.transition_canvas_events(++$scope.transition_count);
    };

    $scope.toggle_cluster_events = function (cluster) {
        toggle_cluster_events(cluster);

        // Now, transition the events
        $scope.transition_canvas_events(++$scope.transition_count);
    };

    $scope.render_plot = function () {
        // Update the axes' labels with the new categories
        $scope.x_label.text($scope.x_param.full_name);
        $scope.y_label.text($scope.y_param.full_name);

        x_data = [];
        y_data = [];

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
        }

        // check for auto-scaling
        x_range = [];
        y_range = [];
        if ($scope.auto_scale) {
            // Lookup ranges to calculate the axes' scaling
            x_range = $scope.x_param.extent;
            y_range = $scope.y_param.extent;
            $scope.user_x_min = $scope.x_param.extent[0];
            $scope.user_x_max = $scope.x_param.extent[1];
            $scope.user_y_min = $scope.y_param.extent[0];
            $scope.user_y_max = $scope.y_param.extent[1];
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
                            x_scale(event[$scope.x_param.fcs_number - 1]),
                            y_scale(event[$scope.y_param.fcs_number - 1]),
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