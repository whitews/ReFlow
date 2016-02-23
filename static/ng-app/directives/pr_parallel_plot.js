app.directive('prparallelplot', function() {
    function link(scope) {
        var width = 260;          // width of the svg element
        var height = 480;         // height of the svg element
        var left_margin = 20;
        var bottom_margin = 40;
        var axes;
        var parameter_extent_dict = {};
        var parameter_scale_functions = {};  // functions for scaling the parameters
        var max_of_the_maxes = 0;
        var colors = d3.scale.category20().range();

        scope.parallel_svg = d3.select("#parallel-plot")
            .append("svg")
            .attr("width", width + left_margin)
            .attr("height", height + bottom_margin);

        scope.initialize_parallel_plot = function(analyzed_parameters, clusters) {
            // clear plot area
            d3.select('#parallel-plot').selectAll("g").remove();
            var plot_area = scope.parallel_svg.append("g")
                .attr("id", "parallel-plot-area")
                .attr("transform", "translate(" + left_margin + ", 5)");

            // determine extent for each analyzed parameter
            var min_value;
            var max_value;
            analyzed_parameters.forEach(function (p) {
                min_value = undefined;
                max_value = undefined;
                clusters.forEach(function(cluster) {
                    for (var cp=0; cp < cluster.parameters.length; cp++) {
                        if (p.fcs_number == cluster.parameters[cp].channel) {
                            if (min_value === undefined) {
                                min_value = cluster.parameters[cp].location;
                            } else if (cluster.parameters[cp].location < min_value) {
                                min_value = cluster.parameters[cp].location;
                            }

                            if (max_value === undefined) {
                                max_value = cluster.parameters[cp].location;
                            } else if (cluster.parameters[cp].location > max_value) {
                                max_value = cluster.parameters[cp].location;
                            }
                        }
                    }
                });

                parameter_scale_functions[p.fcs_number] =
                    d3.scale.linear().domain([min_value, max_value * 1.02])
                        .range([0, width]);
            });

            var line_function = d3.svg.line()
                .x(function (d, i) {
                    return parameter_scale_functions[d.channel](d.location);
                })
                .y(function (d, i ) {
                    return (height * i / (analyzed_parameters.length - 1));
                });

            //scope.plot_data.cluster_data.forEach(function (cluster) {
            scope.parallel_lines = plot_area.append("g")
                .attr('class', 'parallel_lines');

            scope.parallel_lines.selectAll("path")
                .data(scope.plot_data.cluster_data)
                .enter()
                .append("path")
                .attr("id", function (d) {
                    return "cluster_line_" + d.cluster_index;
                })
                .attr('stroke', function (d) {
                    return d.color;
                })
                .attr("d", function (d) {
                    // it's very important we feed the cluster param locations
                    // to line_function in the correct order, which is the
                    // same order as scope.parameters
                    var cluster_locations = [];
                    analyzed_parameters.forEach(function(scope_param) {
                        for (var i = 0; i < d.parameters.length; i++) {
                            if (scope_param.fcs_number == d.parameters[i].channel) {
                                cluster_locations.push(d.parameters[i]);
                                break;
                            }
                        }
                    });
                    return line_function(cluster_locations)
                });

            // put axes (and, more importantly the text) last so it's on top,
            // SVG doesn't use z-index, layers are in order of appearance
            axes = plot_area.selectAll('.axis')
                .data(analyzed_parameters)
                .enter().append('g')
                    .attr("transform", function (d, i) {
                        return "translate(" + width + ", " + (height*i/(analyzed_parameters.length - 1)) + ")";
                    })
                    .attr("class", "axis");

            axes.append('line')
                .attr("x2", function (d) {
                    return -1 * width;
                })
                .attr("stroke", "#a1a1a1")
                .attr("stroke-width", "2")
                .attr("stroke-dasharray", "2, 6");

            axes.append('text')
                .text(function (d) {
                    return d.full_name;
                })
                .attr("text-anchor", "left")
                .attr("transform", function () {
                    return "translate(" + -(width+left_margin) + ", " + 12 + ")";
                })
                .style("font-weight", "bold");
        };
    }

    return {
        link: link,
        controller: 'PRParallelPlotController',
        restrict: 'E',
        replace: true,
        templateUrl: 'static/ng-app/directives/pr_parallel_plot.html'
    };
});

app.controller('PRParallelPlotController', ['$scope', function ($scope) {
    $scope.select_cluster_line = function (cluster) {
        // highlight line in parallel chart
        $scope.parallel_lines.select("#cluster_line_" + cluster.cluster_index)
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

    $scope.deselect_cluster_line = function (cluster) {
        // remove highlight in parallel chart, but not if events are displayed
        if (!cluster.display_events) {
            $scope.parallel_lines.select("#cluster_line_" + cluster.cluster_index)
                .attr("class", "");
        }
    };
}]);