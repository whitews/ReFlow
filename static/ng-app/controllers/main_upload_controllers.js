app.controller(
    'MainSampleUploadController',
    [
        '$scope', '$controller',
        function ($scope, $controller) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});
            $scope.sample_upload_model = {};
        }
    ]
);

var ModalInstanceCtrl = function ($scope, $modalInstance, file) {
    $scope.file = file;
    $scope.ok = function () {
        $modalInstance.close();
    };
};

app.controller(
    'SiteQueryController',
    ['$scope', 'ModelService', function ($scope, ModelService) {

        if ($scope.current_project) {
            getSites();
        }

        $scope.$on('current_project:updated', function () {
            getSites();
        });

        function getSites() {
            $scope.sample_upload_model.sites = ModelService.getSites(
                $scope.current_project.id
            );
        }

        $scope.sample_upload_model.current_site = null;
    }
]);

app.controller(
    'CytometerQueryController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.$on('siteChangedEvent', function () {
            $scope.sample_upload_model.cytometers = ModelService.getCytometers(
                {
                    site: $scope.sample_upload_model.current_site.id
                }
            );
            $scope.sample_upload_model.current_cytometer = null;
        });
    }
]);

app.controller(
    'SubjectQueryController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        if ($scope.current_project) {
            getSubjects();
        }

        $scope.$on('current_project:updated', function () {
            getSubjects();
        });

        function getSubjects() {
            $scope.sample_upload_model.subjects = ModelService.getSubjects(
                $scope.current_project.id
            );
        }
        $scope.sample_upload_model.current_subject = null;
    }
]);

app.controller(
    'VisitTypeQueryController',
    ['$scope', 'ModelService', function ($scope, ModelService) {

        if ($scope.current_project) {
            getVisitTypes();
        }

        $scope.$on('current_project:updated', function () {
            getVisitTypes();
        });

        function getVisitTypes() {
            $scope.sample_upload_model.visit_types = ModelService.getVisitTypes(
                $scope.current_project.id
            );
        }
        $scope.sample_upload_model.current_visit = null;
    }
]);

app.controller(
    'StimulationQueryController',
    ['$scope', 'ModelService', function ($scope, ModelService) {

        if ($scope.current_project) {
            getStimulations();
        }

        $scope.$on('current_project:updated', function () {
            getStimulations();
        });

        function getStimulations() {
            $scope.sample_upload_model.stimulations = ModelService.getStimulations(
                $scope.current_project.id
            );
        }

        $scope.sample_upload_model.current_stimulation = null;
    }
]);

app.controller(
    'SpecimenQueryController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.sample_upload_model.specimens = ModelService.getSpecimens();
    }
]);

app.controller(
    'PretreatmentQueryController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.sample_upload_model.pretreatments = ModelService.getPretreatments();
    }
]);

app.controller(
    'StorageQueryController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.sample_upload_model.storages = ModelService.getStorages();
    }
]);