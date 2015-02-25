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
                $scope.instance = {};
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

            function extractCompFromFCS(header) {
                var reader = new FileReader();
                reader.addEventListener("loadend", function(evt) {
                    var delimiter = evt.target.result[0];
                    var non_paired_list = evt.target.result.split(delimiter);
                    var spill_value = null;
                    var spill_pattern = /spill/i;
                    var spill_text = "";

                    // first match will be empty string since the FCS TEXT
                    // segment starts with the delimiter, so we'll start at
                    // the 2nd index
                    for (var i = 1; i < non_paired_list.length; i+=2) {
                        if (spill_pattern.test(non_paired_list[i])) {
                            spill_value = non_paired_list[i + 1];
                            break;
                        }
                    }

                    if (spill_value != null) {
                        var spill = spill_value.split(',');

                        // 1st value is the matrix size
                        var matrix_size = parseInt(spill.shift());

                        // # of values should be matrix size squared plus
                        // the matrix sized (for the header row)
                        if (spill.length != (matrix_size * matrix_size) + matrix_size) {
                            // Not a parsable matrix!
                            return;
                        }

                        for (var i = 0; i < spill.length; i++) {
                            spill_text += spill[i];
                            if ((i + 1) % matrix_size) {
                                spill_text += '\t';
                            } else {
                                spill_text += '\n';
                            }
                        }
                    }

                    parseCompMatrix(new Blob([spill_text]));
                });
                reader.readAsBinaryString(header);
            }

            $scope.onFileSelect = function ($files) {
                if ($files.length > 0) {
                    $scope.instance.name = $files[0].name;

                    var reader = new FileReader();
                    reader.addEventListener("loadend", function(evt) {
                        var preheader = evt.target.result;

                        if (preheader.substr(0, 3) != 'FCS') {
                            parseCompMatrix($files[0]);
                            return;
                        }

                        // The following uses the FCS standard offset definitions
                        var text_begin = parseInt(preheader.substr(10, 8));
                        var text_end = parseInt(preheader.substr(18, 8));
                        var header = $files[0].slice(text_begin, text_end);

                        // try extracting comp from FCS metadata
                        extractCompFromFCS(header);
                    });
                    var blob = $files[0].slice(0, 58);
                    reader.readAsBinaryString(blob);
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