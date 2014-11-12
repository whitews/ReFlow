app.directive('prscatterplot', function() {
    function link(scope) {
        var width = 620;         // width of the svg element
        var height = 580;         // height of the svg element
        scope.canvas_width = 540;   // width of the canvas
        scope.canvas_height = 540;  // height of the canvas
        var colors = d3.scale.category20();
        var margin = {            // used mainly for positioning the axes' labels
            top: 0,
            right: 0,
            bottom: height - scope.canvas_height,
            left: width - scope.canvas_width
        };
        var cluster_radius = 6;
        scope.transition_ms = 1000;
        scope.heat_base_color = "#5888D0";
        scope.parameters = [];  // flow data column names
        scope.show_heat = false;    // whether to show heat map
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

        scope.$watch('data', function(data) {
            if (!data) {
                return;
            }

            // TODO: check data properties and warn user if they
            // don't look right

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

            scope.data.cluster_data.forEach(function (cluster) {
                // set booleans for controlling the display of a
                // cluster's events & for whether cluster is selected
                cluster.display_events = false;
                cluster.selected = false;
                cluster.color = colors(cluster.cluster_index % 20);

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
            scope.parameters = scope.data.panel_data.parameters;
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
            scope.process_event_data(scope.data.event_data);

            // reset the SVG clusters
            scope.clusters = null;
            cluster_plot_area.selectAll("circle").remove();

            scope.x_param = scope.parameters[0];
            scope.y_param = scope.parameters[0];

            scope.x_pre_scale = '0.01';
            scope.y_pre_scale = '0.01';

            scope.clusters = cluster_plot_area.selectAll("circle").data(scope.data.cluster_data);

            scope.clusters.enter()
                .append("circle")
                .attr("cx", 0)
                .attr("cy", scope.canvas_height)
                .attr("r", cluster_radius)
                .on("mouseover", function(d) {
                    tooltip.style("visibility", "visible");

                    var popup_text = "";

                    // find x_param value
                    d.parameters.forEach(function (p) {
                        if (p.channel == scope.x_param.fcs_number) {
                            popup_text = popup_text + "x: " + (Math.round(p.location * 100) / 100).toString();
                        }
                    });
                    d.parameters.forEach(function (p) {
                        if (p.channel == scope.y_param.fcs_number) {
                            popup_text = popup_text + " y: " + (Math.round(p.location * 100) / 100).toString();
                        }
                    });

                    tooltip.text(popup_text);

                    d.selected = true;

                    scope.$apply();
                })
                .on("mousemove", function() {
                    return tooltip
                        .style(
                        "top",
                            (d3.event.pageY - 10) + "px")
                        .style(
                        "left",
                            (d3.event.pageX + 10) + "px"
                    );
                })
                .on("mouseout", function(d) {
                    d.selected = false;
                    scope.$apply();
                    return tooltip.style("visibility", "hidden");
                })
                .on("click", function(cluster, index) {
                    scope.toggle_cluster_events(cluster);
                    scope.transition_canvas_events(++scope.transition_count);
                });

            scope.render_plot();
        });

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
    }

    return {
        link: link,
        controller: 'PRScatterController',
        restrict: 'E',
        replace: true,
        templateUrl: 'static/ng-app/directives/pr_scatter.html',
        scope: {
            data: '='
        }
    };
});

app.controller('PRScatterController', ['$scope', function ($scope) {
    var x_data;               // x data series to plot
    var y_data;               // y data series to plot
    var x_range;              // used for "auto-range" for chosen x category
    var y_range;              // used for "auto-range" for chosen y category
    var x_scale;              // function to convert x data to svg pixels
    var y_scale;              // function to convert y data to svg pixels

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

    // function to generate sample events in the canvas
    $scope.render_event = function (ctx, pos) {
        ctx.strokeStyle = pos[2];
        ctx.globalAlpha = 1;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(pos[0], pos[1], 1.5, 0, 2 * Math.PI, false);
        ctx.stroke();
    };

    $scope.toggle_cluster_events = function (cluster) {
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

        // render initial data points in the cluster center
        cluster.prev_position = cluster.events.map(function (e) {
            return [x_tmp, y_tmp, cluster.color];
        });
        cluster.prev_position.forEach(function (position) {
            $scope.render_event(cluster.ctx, position);
        });
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
        $scope.compensation = parse_compensation($scope.data.compensation_data);

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
            // overlapping the plot's edge
            p.extent[0] = p.extent[0] - (p.extent[1] - p.extent[0]) * 0.02;
            p.extent[1] = p.extent[1] + (p.extent[1] - p.extent[0]) * 0.02;
        });

        event_objects.forEach(function (e) {
            for (var i = 0; i < $scope.data.cluster_data.length; i++) {
                if ($scope.data.cluster_data[i].event_indices.indexOf(e.event_index) !== -1) {
                    $scope.data.cluster_data[i].events.push(e);
                    break;
                }
            }
        });
    };

    $scope.render_plot = function () {
        // Update the axes' labels with the new categories
        $scope.x_label.text($scope.x_param.full_name);
        $scope.y_label.text($scope.y_param.full_name);

        x_data = [];
        y_data = [];

        // Populate x_data and y_data using chosen x & y parameters
        for (var i=0, len=$scope.data.cluster_data.length; i<len; i++) {
            $scope.data.cluster_data[i].parameters.forEach(function (p) {
                if (p.channel == $scope.x_param.fcs_number) {
                    x_data[i] = p.location;
                }
                if (p.channel == $scope.y_param.fcs_number) {
                    y_data[i] = p.location;
                }
            });
        }

        // Lookup ranges to calculate the axes' scaling
        x_range = $scope.x_param.extent;
        y_range = $scope.y_param.extent;

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
        $scope.data.cluster_data.forEach(function (cluster) {
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
                            $scope.render_event(cluster.ctx, position);
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
                        $scope.render_event(cluster.ctx, position);
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
