/**
 * Created by swhite on 4/7/14.
 */
app.controller(
    'SitePanelController',
    [
        '$scope',
        '$modal',
        'SitePanel',
        function ($scope, $modal, SitePanel) {
            $scope.model.site_panel_url = '/static/ng-fcs-upload-app/partials/create_site_panel.html';
            $scope.model.some_var = "Do site panel stuff here";

            $scope.changeSomething = function () {
                $scope.model.some_var = "You changed something!";
            };

        }
    ]
);
