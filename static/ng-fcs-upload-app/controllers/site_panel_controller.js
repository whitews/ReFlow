/**
 * Created by swhite on 4/7/14.
 */
app.controller(
    'SitePanelController',
    [
        '$scope',
        'SitePanel',
        function ($scope, SitePanel) {
            $scope.model.site_panel_url = '/static/ng-fcs-upload-app/partials/create_site_panel.html';
            $scope.model.some_var = "Do site panel stuff here";
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
        });
    }
]);