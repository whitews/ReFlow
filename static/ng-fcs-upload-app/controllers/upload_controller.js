/**
 * Created by swhite on 2/25/14.
 */
app.controller(
    'UploadController',
    [
        '$scope',
        'Project',
        'Site',
        'Specimen',
        'Cytometer',
        'Pretreatment',
        'Storage',
        function ($scope, Project, Site, Specimen, Cytometer, Pretreatment, Storage) {
            $scope.projects = Project.query();
            $scope.specimens = Specimen.query();
            $scope.pretreatments = Pretreatment.query();
            $scope.storages = Storage.query();

            $scope.projectChanged = function () {
                $scope.sites = Site.query({project: $scope.current_project.id});
                $scope.current_site = null;
                $scope.current_cytometer = null;
            };

            $scope.siteChanged = function () {
                $scope.cytometers = Cytometer.query({site: $scope.current_site.id});
                $scope.current_cytometer = null;
            };

        }
    ]
);