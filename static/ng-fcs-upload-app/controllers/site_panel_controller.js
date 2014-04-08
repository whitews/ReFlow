/**
 * Created by swhite on 4/7/14.
 */
app.controller(
    'SitePanelController',
    [
        '$scope',
        '$timeout',
        '$modal',
        'SitePanel',
        function ($scope, $timeout, $modal, SitePanel) {
            $scope.model.some_var = "Do stuff here"

        }
    ]
);
