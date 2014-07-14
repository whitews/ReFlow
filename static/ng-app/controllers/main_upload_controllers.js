/**
 * Created by swhite on 7/3/14.
 */

app.controller(
    'MainSampleUploadController',
    [
        '$scope', '$controller', 'ModelService',
        function ($scope, $controller, ModelService) {
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
    ['$scope', 'Site', function ($scope, Site) {
        $scope.sample_upload_model.sites = Site.query({project: $scope.current_project.id});
        $scope.sample_upload_model.current_site = null;
    }
]);

app.controller(
    'CytometerQueryController',
    ['$scope', 'Cytometer', function ($scope, Cytometer) {
        $scope.$on('siteChangedEvent', function () {
            $scope.sample_upload_model.cytometers = Cytometer.query({site: $scope.sample_upload_model.current_site.id});
            $scope.sample_upload_model.current_cytometer = null;
        });
    }
]);

app.controller(
    'SubjectQueryController',
    ['$scope', 'Subject', function ($scope, Subject) {
        $scope.sample_upload_model.subjects = Subject.query({project: $scope.current_project.id});
        $scope.sample_upload_model.current_subject = null;
    }
]);

app.controller(
    'VisitTypeQueryController',
    ['$scope', 'VisitType', function ($scope, VisitType) {
        $scope.sample_upload_model.visit_types = VisitType.query({project: $scope.current_project.id});
        $scope.sample_upload_model.current_visit = null;
    }
]);

app.controller(
    'StimulationQueryController',
    ['$scope', 'Stimulation', function ($scope, Stimulation) {
        $scope.sample_upload_model.stimulations = Stimulation.query({project: $scope.current_project.id});
        $scope.sample_upload_model.current_stimulation = null;
    }
]);

app.controller(
    'SpecimenQueryController',
    ['$scope', 'Specimen', function ($scope, Specimen) {
        $scope.sample_upload_model.specimens = Specimen.query();
    }
]);

app.controller(
    'PretreatmentQueryController',
    ['$scope', 'Pretreatment', function ($scope, Pretreatment) {
        $scope.sample_upload_model.pretreatments = Pretreatment.query();
    }
]);

app.controller(
    'StorageQueryController',
    ['$scope', 'Storage', function ($scope, Storage) {
        $scope.sample_upload_model.storages = Storage.query();
    }
]);