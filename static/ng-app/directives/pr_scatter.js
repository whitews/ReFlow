app.directive('prscatterplot', function() {
    function link(scope, el, attr) {
        var width = 620;         // width of the svg element
        var height = 580;         // height of the svg element
        scope.canvas_width = 540;   // width of the canvas
        scope.canvas_height = 540;  // height of the canvas
        var margin = {            // used mainly for positioning the axes' labels
            top: 0,
            right: 0,
            bottom: height - scope.canvas_height,
            left: width - scope.canvas_width
        };
        scope.x_cat;                // chosen plot parameter for x-axis
        scope.y_cat;                // chosen plot parameter for y-axis
        scope.x_transform;          // chosen transform for x-data
        scope.y_transform;          // chosen transform for y-data
        scope.show_heat = false;    // whether to show heat map
        scope.x_pre_scale;          // pre-scale factor for x data
        scope.y_pre_scale;          // pre-scale factor for y data
        scope.clusters;
        var cluster_radius = 4.5;
        scope.transition_ms = 2000;
        var x_data;               // x data series to plot
        var y_data;               // y data series to plot
        var x_range;              // used for "auto-range" for chosen x category
        var y_range;              // used for "auto-range" for chosen y category
        var x_scale;              // function to convert x data to svg pixels
        var y_scale;              // function to convert y data to svg pixels
        var flow_data;            // FCS data
        scope.parameter_list = [];  // flow data column names
        var subsample_count = 10000;  // Number of events to subsample

        // Transition variables
        scope.prev_position = [];         // prev_position [x, y, color] pairs
        scope.transition_count = 0;       // used to cancel old transitions

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

            // reset the parameter list
            scope.parameter_list = [];

            // Grab our column names
            scope.data.cluster_data[0].parameters.forEach(function (p) {
                scope.parameter_list.push(p.channel);
            });

            scope.x_cat = scope.parameter_list[0];
            scope.y_cat = scope.parameter_list[0];

            scope.x_pre_scale = '0.01';
            scope.y_pre_scale = '0.01';

            // render initial data points in the center of plot
            scope.prev_position = scope.data.cluster_data.map(function (d) {
                return [scope.canvas_width / 2, scope.canvas_height / 2, "rgba(96, 96, 212, 1.0)"];
            });
            scope.prev_position.forEach(scope.circle);

            scope.clusters = cluster_plot_area.selectAll("circle").data(scope.data.cluster_data);

            scope.clusters.enter()
                .append("circle")
                .attr("cx", 0)
                .attr("cy", 0)
                .attr("r", cluster_radius)
                .on("mouseover", function(d) {
                    tooltip.style("visibility", "visible");

                    var popup_text = "";

                    // find x_cat value
                    d.parameters.forEach(function (p) {
                        if (p.channel == scope.x_cat) {
                            popup_text = popup_text + "x: " + (Math.round(p.location * 100) / 100).toString();
                        }
                    });
                    d.parameters.forEach(function (p) {
                        if (p.channel == scope.y_cat) {
                            popup_text = popup_text + " y: " + (Math.round(p.location * 100) / 100).toString();
                        }
                    });

                    tooltip.text(popup_text);
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
                .on("mouseout", function() {
                    return tooltip.style("visibility", "hidden");
                })
                .on("click", function(cluster, index) {
                    console.log("clicked a cluster!");
                });

            scope.render_plot();
        });

        scope.svg = d3.select("#scatterplot")
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("style", "z-index: 1000");

        // create canvas for plot, it'll just be square as the axes will be drawn
        // using svg...will have a top and right margin though
        d3.select("#scatterplot")
            .append("canvas")
            .attr("id", "canvas_plot")
            .attr("style", "position:absolute;left: " + margin.left + "px; top: " + margin.top + "px;")
            .attr("width", scope.canvas_width)
            .attr("height", scope.canvas_height);

        var canvas = document.getElementById("canvas_plot");

        scope.ctx = canvas.getContext('2d');

        // render circle in canvas for each data point
        scope.circle = function (pos) {
            scope.ctx.strokeStyle = pos[2];
            scope.ctx.globalAlpha = 1;
            scope.ctx.lineWidth = 2;
            scope.ctx.beginPath();
            scope.ctx.arc(pos[0], pos[1], 4.5, 0, 2 * Math.PI, false);
            scope.ctx.stroke();
        };

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

        // Heat map stuff
        scope.heat_map_data = [];
        d3.select("#scatterplot")
            .append("canvas")
            .attr("id", "heat_map_canvas")
            .attr("style", "position:absolute;left: " + margin.left + "px; top: " + margin.top + "px;")
            .attr("width", scope.canvas_width)
            .attr("height", scope.canvas_height);

        var heat_map_canvas = document.getElementById("heat_map_canvas");
        scope.heat_map_ctx = heat_map_canvas.getContext('2d');

        var heat_cfg = {
            canvas: heat_map_canvas,
            radius: 5
        };

        scope.heat_map = heat.create(heat_cfg);
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

    function asinh(number) {
        return Math.log(number + Math.sqrt(number * number + 1));
    }

    $scope.render_plot = function () {
        // Determine whether user wants to see the heat map
        show_heat = $("#heat_map_checkbox").is(':checked');

        // Update the axes' labels with the new categories
        $scope.x_label.text($scope.x_cat);
        $scope.y_label.text($scope.y_cat);

        x_data = [];
        y_data = [];

        // Populate x_data and y_data using chosen x & y parameters
        for (var i=0, len=$scope.data.cluster_data.length; i<len; i++) {
            $scope.data.cluster_data[i].parameters.forEach(function (p) {
                if (p.channel == $scope.x_cat) {
                    x_data[i] = p.location;
                }
                if (p.channel == $scope.y_cat) {
                    y_data[i] = p.location;
                }
            });
        }

        // Get the new ranges to calculate the axes' scaling
        x_range = d3.extent(x_data, function (d) {
            return parseFloat(d);
        });
        y_range = d3.extent(y_data, function (d) {
            return parseFloat(d);
        });

        // pad ranges a bit, keeps the data points from overlapping the plot's edge
        x_range[0] = x_range[0] - (x_range[1] - x_range[0]) * 0.1;
        x_range[1] = x_range[1] + (x_range[1] - x_range[0]) * 0.1;
        y_range[0] = y_range[0] - (y_range[1] - y_range[0]) * 0.1;
        y_range[1] = y_range[1] + (y_range[1] - y_range[0]) * 0.1;

        // Update scaling functions for determining placement of the x and y axes
        x_scale = d3.scale.linear().domain(x_range).range([0, $scope.canvas_width]);
        y_scale = d3.scale.linear().domain(y_range).range([$scope.canvas_height, 0]);

        // Update axes with the proper scaling
        $scope.x_axis.call(d3.svg.axis().scale(x_scale).orient("bottom"));
        $scope.y_axis.call(d3.svg.axis().scale(y_scale).orient("left"));

        // Clear heat map canvas before the transitions
        $scope.heat_map_ctx.clearRect(
            0, 0, $scope.heat_map_ctx.canvas.width, $scope.heat_map_ctx.canvas.height);
        $scope.heat_map_data = [];

        // transition clusters
        $scope.clusters.transition().duration($scope.transition_ms)
            .attr("cx", function (d) {
                for (var i=0; i < d.parameters.length; i++) {
                    if (d.parameters[i].channel == $scope.x_cat) {
                        return x_scale(d.parameters[i].location);
                    }
                }
            })
            .attr("cy", function (d) {
                for (var i=0; i < d.parameters.length; i++) {
                    if (d.parameters[i].channel == $scope.y_cat) {
                        return y_scale(d.parameters[i].location);
                    }
                }
            });

        transition(++$scope.transition_count);
    };

    function transition(count) {
        // calculate next positions
        var next_position = [];
        for (var i = 0, len = $scope.data.cluster_data.length; i < len; i++) {
            var x = x_scale(x_data[i]);
            var y = y_scale(y_data[i]);
            var color = "rgba(96, 96, 212, 1.0)";

            next_position.push([x, y, color]);
        }

        var interpolator = d3.interpolate($scope.prev_position, next_position);

        // run transition
        d3.timer(function (t) {
            // Clear canvas
            // Use the identity matrix while clearing the canvas
            $scope.ctx.clearRect(0, 0, $scope.ctx.canvas.width, $scope.ctx.canvas.height);

            // abort old transition
            if (count < $scope.transition_count) return true;

            // transition for time t, in milliseconds
            if (t > 2000) {
                $scope.prev_position = next_position;
                $scope.prev_position.forEach($scope.circle);

                if ($scope.show_heat) {
                    $scope.heat_map_ctx.clearRect(
                        0,
                        0,
                        $scope.heat_map_ctx.canvas.width,
                        $scope.heat_map_ctx.canvas.height
                    );

                    $scope.prev_position.forEach(function (pos) {
                        $scope.heat_map_data.push({x: pos[0], y: pos[1]});
                    });

                    $scope.heat_map.set_data($scope.heat_map_data);
                    $scope.heat_map.colorize();
                }

                return true
            }

            $scope.prev_position = interpolator(t / 2000);
            $scope.prev_position.forEach($scope.circle);

            return false;
        });
    }
}]);

