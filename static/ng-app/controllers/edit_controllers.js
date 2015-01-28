app.controller(
    'ProjectEditController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.current_project = ModelService.current_project;

            $scope.create_update = function (instance) {
                $scope.errors = [];
                var response = ModelService.createUpdateProject(instance);

                response.$promise.then(function (object) {
                    // notify to update project list
                    ModelService.projectsUpdated();

                    // also check if this is the current project
                    if ($scope.current_project) {
                        if (object.id == $scope.current_project.id) {
                            ModelService.setCurrentProjectById(object.id);
                        }
                    }

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
    'SubjectGroupEditController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.current_project;

        $scope.create_update = function (instance) {
            $scope.errors = [];
            if (!instance.id) {
                instance.project = $scope.current_project.id;
            }

            var response = ModelService.createUpdateSubjectGroup(instance);

            response.$promise.then(function () {
                // notify to update list
                ModelService.subjectGroupsUpdated();

                // close modal
                $scope.ok();

            }, function (error) {
                $scope.errors = error.data;
            });
        };
    }
]);

app.controller(
    'SubjectEditController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.current_project;
        $scope.subject_groups = ModelService.getSubjectGroups(
            $scope.current_project.id
        );

        $scope.create_update = function (instance) {
            $scope.errors = [];
            if (!instance.id) {
                instance.project = $scope.current_project.id;
            }

            var response = ModelService.createUpdateSubject(instance);

            response.$promise.then(function () {
                // notify to update list
                ModelService.subjectsUpdated();

                // close modal
                $scope.ok();

            }, function (error) {
                $scope.errors = error.data;
            });
        };
    }
]);

app.controller(
    'SiteEditController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.current_project;

        $scope.create_update = function (instance) {
            $scope.errors = [];
            if (!instance.id) {
                instance.project = $scope.current_project.id;
            }

            var response = ModelService.createUpdateSite(instance);

            response.$promise.then(function () {
                // notify to update list
                ModelService.sitesUpdated();

                // close modal
                $scope.ok();

            }, function (error) {
                $scope.errors = error.data;
            });
        };
    }
]);

app.controller(
    'CytometerEditController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.current_project = ModelService.current_project;

            // get list of sites user has permission for new cytometers
            // existing cytometers cannot change their site
            if ($scope.instance == null) {
                $scope.sites = ModelService.getProjectSitesWithAddPermission(
                    $scope.current_project.id
                );
            }

            $scope.create_update = function (instance) {
                $scope.errors = [];
                var response = ModelService.createUpdateCytometer(instance);

                response.$promise.then(function () {
                    // notify to update list
                    ModelService.cytometersUpdated();

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
    'VisitTypeEditController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.current_project;

        $scope.create_update = function (instance) {
            $scope.errors = [];
            if (!instance.id) {
                instance.project = $scope.current_project.id;
            }

            var response = ModelService.createUpdateVisitType(instance);

            response.$promise.then(function () {
                // notify to update list
                ModelService.visitTypesUpdated();

                // close modal
                $scope.ok();

            }, function (error) {
                $scope.errors = error.data;
            });
        };
    }
]);

app.controller(
    'CellSubsetLabelEditController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.current_project;

        $scope.create_update = function (instance) {
            $scope.errors = [];
            if (!instance.id) {
                instance.project = $scope.current_project.id;
            }

            var response = ModelService.createUpdateCellSubsetLabel(instance);

            response.$promise.then(function () {
                // notify to update list
                ModelService.cellSubsetLabelsUpdated();

                // close modal
                $scope.ok();

            }, function (error) {
                $scope.errors = error.data;
            });
        };
    }
]);

app.controller(
    'StimulationEditController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        $scope.current_project = ModelService.current_project;

        $scope.create_update = function (instance) {
            $scope.errors = [];
            if (!instance.id) {
                instance.project = $scope.current_project.id;
            }

            var response = ModelService.createUpdateStimulation(instance);

            response.$promise.then(function () {
                // notify to update list
                ModelService.stimulationsUpdated();

                // close modal
                $scope.ok();

            }, function (error) {
                $scope.errors = error.data;
            });
        };
    }
]);

app.controller(
    'SampleEditController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.current_project = ModelService.current_project;

            $scope.subjects = ModelService.getSubjects(
                $scope.current_project.id
            );
            $scope.visit_types = ModelService.getVisitTypes(
                $scope.current_project.id
            );
            $scope.stimulations = ModelService.getStimulations(
                $scope.current_project.id
            );

            $scope.specimens = ModelService.getSpecimens();
            $scope.pretreatments = ModelService.getPretreatments();
            $scope.storages = ModelService.getStorages();

            $scope.update = function (instance) {
                $scope.errors = [];
                var response = ModelService.createUpdateSample(instance);

                response.$promise.then(function () {
                    // notify to update list
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

            // everything but bead panels
            var PANEL_TYPES = ['FS', 'US', 'FM', 'IS'];

            $scope.panel_templates = ModelService.getPanelTemplates(
                {
                    'project': $scope.current_project.id,
                    'staining': PANEL_TYPES
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