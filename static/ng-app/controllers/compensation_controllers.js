app.controller(
    'CompensationController',
    [
        '$scope',
        '$q',
        '$controller',
        '$modal',
        'ModelService',
        function ($scope, $q, $controller, $modal, ModelService) {
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

            $scope.show_matrix = function(instance) {
                $scope.errors = [];

                // launch form modal
                $modal.open({
                    templateUrl: MODAL_URLS.COMPENSATION_MATRIX,
                    controller: 'ModalFormCtrl',
                    size: 'lg',
                    resolve: {
                        instance: function() {
                            return instance;
                        }
                    }
                });
            };
        }
    ]
);

app.controller(
    'CompensationEditController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.current_project = ModelService.current_project;
            $scope.errors = [];
            $scope.matrix_errors = [];

            // get list of sites user has permission for new cytometers
            // existing cytometers cannot change their site
            if ($scope.instance == null) {
                $scope.sites = ModelService.getProjectSitesWithAddPermission(
                    $scope.current_project.id
                );
            }

            $scope.panel_templates = ModelService.getPanelTemplates(
                {
                    'project': $scope.current_project.id
                }
            );

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

            function validateCompMatrix(comp_obj) {
                // check the row count and row element counts match header
                var header_length = comp_obj.headers.length;
                if (comp_obj.data.length != header_length) {
                    $scope.matrix_errors.push('Number of rows does not match the number of parameters');
                    return false;
                }
                for (var i = 0; i < comp_obj.data.length; i++) {
                    if (comp_obj.data[i].length != header_length) {
                        $scope.matrix_errors.push('Number of columns does not match the number of parameters');
                        return false;
                    }
                }
                return true;
            }

            function parseCompMatrix(f) {
                var reader = new FileReader();
                var comp_obj = {
                    headers: [],
                    data: []
                };
                $scope.errors = [];
                $scope.matrix_errors = [];
                reader.addEventListener("loadend", function(evt) {
                    var rows = evt.target.result.split('\n');

                    // real_rows stored all non-empty rows
                    var real_rows = [];
                    rows.forEach(function(r) {
                        if (r !== "") {
                            real_rows.push(r);
                        }
                    });
                    var header_row = real_rows.shift();
                    comp_obj.headers = header_row.split('\t');

                    // parse data rows
                    real_rows.forEach(function (row) {
                        comp_obj.data.push(row.split('\t'));
                    });
                    if (validateCompMatrix(comp_obj)) {
                        $scope.instance.matrix_text = evt.target.result
                    }
                    $scope.$apply();
                });
                reader.readAsText(f);
            }

            $scope.onFileSelect = function ($files) {
                if ($files.length > 0) {
                    $scope.instance.name = $files[0].name;
                    parseCompMatrix($files[0]);
                }
            };

            $scope.create = function () {
                $scope.errors = [];
                var data = {
                    'name': $scope.instance.name,
                    'panel_template': $scope.instance.panel_template,
                    'site': $scope.instance.site,
                    'matrix_text': $scope.instance.matrix_text,
                    'acquisition_date':
                            $scope.instance.acquisition_date.getFullYear().toString() +
                            "-" +
                            ($scope.instance.acquisition_date.getMonth() + 1) +
                            "-" +
                            $scope.instance.acquisition_date.getDate().toString()
                };
                var response = ModelService.createCompensation(data);

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