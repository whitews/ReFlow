app.directive('prparallelplot', function() {
    function link(scope) {
        var width = 260;          // width of the svg element
        var height = 520;         // height of the svg element
        var axes;
        var parameter_extent_dict = {};
        var parameter_scale_functions = {};  // functions for scaling the parameters
        var max_of_the_maxes = 0;
        var colors = d3.scale.category20().range();

        scope.parallel_svg = d3.select("#parallel-plot")
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("style", "border: 1px solid #a1a1a1");

        var plot_area = scope.parallel_svg.append("g")
            .attr("id", "parallel-plot-area");

        scope.initialize_parallel_plot = function() {
            // get individual parameter scale functions
            scope.parameters.forEach(function (p) {
                parameter_scale_functions[p.fcs_number] =
                    d3.scale.linear().domain(p.extent)
                        .range([0, width]);

            });

            axes = plot_area.selectAll('.axis')
                .data(scope.parameters)
                .enter().append('g')
                    .attr("transform", function (d, i) {
                        return "rotate(-90) translate(0, " + (width*i/scope.parameters.length) + ")";
                    })
                    .attr("class", "axis");

            axes.append('line')
                    .attr("x2", function (d) {
                        return -1 * parameter_scale_functions[d.fcs_number](d.extent[1]);
                    });

            axes.append('text')
                    .text(function (d) {
                        return d.full_name;
                    })
                    .attr("text-anchor", "middle")
                    .attr("transform", function () {
                        return "rotate(" + 90 + ")" +
                            " translate(" + 0 + ", " + 20 + ")";
                    });

            scope.plot_data.cluster_data.forEach(function (cluster) {
                var series = plot_area.append("g")
                    .attr('class', 'series')
                    .style('stroke', function () {
                        return cluster.color;
                    });

                var series_array = [];
                scope.parameters.forEach(function (p) {
                    series_array.push(cluster.parameters);
                });

                var lineFunction = d3.svg.line()
                    .x(function (d, i ) {
                        return (width * i / scope.parameters.length);
                    })
                    .y(function (d, i) {
                        return parameter_scale_functions[scope.parameters[i]](d);
                    });

                series.append('path')
                    .attr("class", "data-line")
                    .attr("d", lineFunction(series_array));
            });


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