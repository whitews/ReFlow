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

        scope.initialize_parallel_plot = function() {
            // clear plot area
            d3.select('#parallel-plot').selectAll("g").remove();
            var plot_area = scope.parallel_svg.append("g")
                .attr("id", "parallel-plot-area")
                .attr("transform", "translate(" + left_margin + ", 5)");

            // get individual parameter scale functions, but we must take
            // care to skip channels that were not analyzed since there
            // are no cluster locations for those channels
            // TODO: should all this analyzed cluster stuff be in parent ctrl?
            var analyzed_parameters = [];
            var example_cluster = scope.plot_data.cluster_data[0];
            scope.parameters.forEach(function (param) {
                // use the 1st cluster params for comparison
                for (var i=0; i<example_cluster.parameters.length; i++) {
                    if (param.fcs_number == example_cluster.parameters[i].channel) {
                        analyzed_parameters.push(param);
                        break;
                    }
                }
            });
            analyzed_parameters.forEach(function (p) {
                parameter_scale_functions[p.fcs_number] =
                    d3.scale.linear().domain(p.extent)
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
                    scope.parameters.forEach(function(scope_param) {
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
                    return -1 * parameter_scale_functions[d.fcs_number](d.extent[1]);
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

            scope.render_parallel_plot();
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
    $scope.render_parallel_plot = function () {

    };
}]);