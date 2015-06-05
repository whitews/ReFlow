app.controller(
    'CompensationController',
    [
        '$scope',
        '$q',
        '$controller',
        'ModelService',
        function ($scope, $q, $controller, ModelService) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            function populate_compensations() {
                var sites_can_add = ModelService.getProjectSitesWithAddPermission(
                    $scope.current_project.id
                ).$promise;

                var sites_can_modify = ModelService.getProjectSitesWithModifyPermission(
                    $scope.current_project.id
                ).$promise;

                var compensations = ModelService.getCompensations(
                    {
                        'project': $scope.current_project.id
                    }
                ).$promise;

                $q.all([sites_can_add, sites_can_modify, compensations]).then(function (objects) {
                    $scope.compensations = objects[2];

                    // user has add privileges on at least one site
                    if (objects[0].length > 0) {
                        $scope.can_add_data = true;
                    }

                    $scope.compensations.forEach(function (c) {
                        c.can_modify = false;

                        // check if compensation's site is in modify list
                        for (var i=0; i<objects[1].length; i++) {
                            if (c.site == objects[1][i].id) {
                                c.can_modify = true;
                                break;
                            }
                        }
                    });
                });
            }

            if ($scope.current_project != undefined) {
                populate_compensations();
            }
            $scope.$on('current_project:updated', function () {
                populate_compensations();
            });

            $scope.$on('compensations:updated', function () {
                populate_compensations();
            });
        }
    ]
);

app.controller(
    'CompensationFromSampleController',
    [
        '$scope',
        '$modalInstance',
        'instance',
        'ModelService',
        function ($scope, $modalInstance, instance, ModelService) {
            // Note: $scope.instance in this case is an FCS sample so
            // create a separate comp_instance
            $scope.comp_instance = {};
            $scope.comp_instance.name = instance.original_filename;
            $scope.comp_instance.acquisition_date = new Date(
                instance.acquisition_date.substr(0, 4),
                parseInt(instance.acquisition_date.substr(5, 2)) - 1,
                parseInt(instance.acquisition_date.substr(8, 2))
            );
            $scope.comp_instance.site_panel = instance.site_panel;

            $scope.ok = function () {
                $modalInstance.close();
            };

            $scope.errors = [];
            $scope.matrix_errors = [];

            // Date picker stuff
            $scope.today = function() {
                $scope.dt = new Date();
            };
            $scope.today();

            $scope.clear = function () {
                $scope.dt = null;
            };

            $scope.open = function($event) {
                $event.preventDefault();
                $event.stopPropagation();

                $scope.datepicker_open = true;
            };

            $scope.dateOptions = {
                'year-format': "'yy'",
                'starting-day': 1,
                'show-weeks': false
            };

            $scope.formats = ['dd-MMMM-yyyy', 'yyyy/MM/dd', 'shortDate'];
            $scope.format = $scope.formats[0];
            // End date picker stuff

            // see if sample's metadata has a spill key/value
            var fcs_spill = ModelService.getSampleMetadata({
                'sample': instance.id,
                'key': 'spill'
            });

            fcs_spill.$promise.then(function(data) {
                if (data.length > 0) {
                    var spill = data[0].value.split(',');

                    // 1st value is the matrix size
                    var matrix_size = parseInt(spill.shift());

                    // # of values should be matrix size squared plus
                    // the matrix sized (for the header row)
                    if (spill.length != (matrix_size * matrix_size) + matrix_size) {
                        // Not a parsable matrix!
                        return;
                    }

                    var spill_text = '';
                    for (var i = 0; i < spill.length; i++) {
                        spill_text += spill[i];
                        if ((i + 1) % matrix_size) {
                            spill_text += '\t';
                        } else {
                            spill_text += '\n';
                        }
                    }
                    $scope.comp_instance.matrix_text = spill_text;
                }
            });

            $scope.create = function () {
                $scope.errors = [];
                var data = {
                    'name': $scope.comp_instance.name,
                    'site_panel': $scope.comp_instance.site_panel,
                    'matrix_text': $scope.comp_instance.matrix_text,
                    'acquisition_date':
                            $scope.comp_instance.acquisition_date.getFullYear().toString() +
                            "-" +
                            ($scope.comp_instance.acquisition_date.getMonth() + 1) +
                            "-" +
                            $scope.comp_instance.acquisition_date.getDate().toString()
                };
                var response = ModelService.createCompensation(data);

                response.$promise.then(function () {
                    // notify to update comp list
                    ModelService.compensationsUpdated();
                    ModelService.samplesUpdated();

                    // close modal
                    $scope.ok();

                }, function (error) {
                    $scope.errors = error.data;
                });
            };
        }
    ]
);

app.controller(
    'CompensationDeleteController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.destroy = function (instance) {
                var response = ModelService.destroyCompensation(instance);

                response.$promise.then(function () {
                    // notify to update comp list
                    ModelService.compensationsUpdated();

                    // close modal
                    $scope.ok();

                }, function (error) {
                    $scope.errors = error.data;
                });
            };
        }
    ]
);