/**
 * Created by swhite on 2/25/14.
 */
app.controller(
    'UploadController',
    [
        '$scope',
        '$timeout',
        '$upload',
        'Project',
        'Site',
        'Specimen',
        'Cytometer',
        'Pretreatment',
        'Storage',
        'Stimulation',
        'VisitType',
        'Subject',
        'SitePanel',
        function ($scope, $timeout, $upload, Project, Site, Specimen, Cytometer, Pretreatment, Storage, Stimulation, VisitType, Subject, SitePanel) {
            $scope.projects = Project.query();
            $scope.specimens = Specimen.query();
            $scope.pretreatments = Pretreatment.query();
            $scope.storages = Storage.query();

            $scope.projectChanged = function () {
                $scope.sites = Site.query({project: $scope.current_project.id});
                $scope.current_site = null;
                $scope.current_cytometer = null;
                $scope.stimulations = Stimulation.query({project: $scope.current_project.id});
                $scope.visit_types = VisitType.query({project: $scope.current_project.id});
                $scope.subjects = Subject.query({project: $scope.current_project.id});
            };

            $scope.siteChanged = function () {
                $scope.cytometers = Cytometer.query({site: $scope.current_site.id});
                $scope.current_cytometer = null;
                $scope.site_panels = SitePanel.query({project_panel__project: $scope.current_project.id});
            };
            
            $scope.acquisitionDateChanged = function () {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    if ($scope.file_queue[i].selected) {
                        $scope.file_queue[i].acquisition_date = $scope.current_acquisition_date;
                    }
                }
            };

            $scope.sitePanelChanged = function (selected) {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    if ($scope.file_queue[i].selected) {
                        $scope.file_queue[i].site_panel = selected;
                    }
                }
            };
            
            $scope.subjectChanged = function (selected) {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    if ($scope.file_queue[i].selected) {
                        $scope.file_queue[i].subject = selected;
                    }
                }
            };
            
            $scope.visitTypeChanged = function (selected) {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    if ($scope.file_queue[i].selected) {
                        $scope.file_queue[i].visit_type = selected;
                    }
                }
            };
            
            $scope.stimulationChanged = function (selected) {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    if ($scope.file_queue[i].selected) {
                        $scope.file_queue[i].stimulation = selected;
                    }
                }
            };
            
            $scope.specimenChanged = function (selected) {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    if ($scope.file_queue[i].selected) {
                        $scope.file_queue[i].specimen = selected;
                    }
                }
            };
            
            $scope.pretreatmentChanged = function (selected) {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    if ($scope.file_queue[i].selected) {
                        $scope.file_queue[i].pretreatment = selected;
                    }
                }
            };
            
            $scope.storageChanged = function (selected) {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    if ($scope.file_queue[i].selected) {
                        $scope.file_queue[i].storage = selected;
                    }
                }
            };

            // file reader stuff
            $scope.fileReaderSupported = window.FileReader != null;
            $scope.hasUploader = function(index) {
                return $scope.upload[index] != null;
            };
            $scope.abort = function(index) {
                $scope.upload[index].abort();
                $scope.upload[index] = null;
            };

            $scope.toggleAllFiles = function () {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    $scope.file_queue[i].selected = $scope.master_checkbox;
                }
            };

            function setupReader(obj) {
                var reader = new FileReader();
                reader.addEventListener("loadend", function(evt) {
                    var preheader = evt.target.result;

                    if (preheader.substr(0, 3) != 'FCS') {
                        return;
                    }

                    // The following uses the FCS standard offset definitions
                    obj.text_begin = parseInt(preheader.substr(10, 8));
                    obj.text_end = parseInt(preheader.substr(18, 8));
                    obj.data_begin = parseInt(preheader.substr(26, 8));
                    obj.data_end = parseInt(preheader.substr(34, 8));

                    parseFcsText(obj);
                });
                var blob = obj.file.slice(0, 58);
                reader.readAsBinaryString(blob);
            }

            function parseFcsText(obj) {
                var reader = new FileReader();
                reader.addEventListener("loadend", function(evt) {
                    var delimiter = evt.target.result[0];
                    var non_paired_list = evt.target.result.split(delimiter);
                    obj.metadata = [];

                    // first match will be empty string since the FCS TEXT
                    // segment starts with the delimiter, so we'll start at
                    // the 2nd index
                    for (var i = 1; i < non_paired_list.length; i+=2) {
                        obj.metadata.push(
                            {
                                key: non_paired_list[i],
                                value: non_paired_list[i+1]
                            }
                        );
                    }

                    // Using $apply here to trigger template update
                    $scope.$apply(function () {
                        $scope.file_queue.push(obj);
                    });
                });

                var blob = obj.file.slice(obj.text_begin, obj.text_end);
                reader.readAsBinaryString(blob);
            }

            $scope.onFileSelect = function($files) {
                $scope.file_queue = [];
                $scope.current_acquisition_date = "";

                for (var i = 0; i < $files.length; i++) {
                    setupReader({
                        filename: $files[i].name,
                        file: $files[i],
                        metadata: {},
                        selected: false,
                    });
                }
            };

            $scope.uploadSelected = function() {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    if ($scope.file_queue[i].selected) {
                        upload(i);
                    }
                }
            };

            function upload(index) {
                $scope.file_queue[index].progress = 0;

                $scope.file_queue[index].progress = $upload.upload({
                    url : '/api/repository/samples/add/',
                    method: 'POST',
//                            headers: {'myHeaderKey': 'myHeaderVal'},

                    // put the sample's model data here
                    data : {
                        'subject': $scope.file_queue[index].subject.id,
                        'visit': $scope.file_queue[index].visit_type.id,
                        'specimen': $scope.file_queue[index].specimen.id,
                        'pretreatment': $scope.file_queue[index].pretreatment.name,
                        'storage': $scope.file_queue[index].storage.name,
                        'stimulation': $scope.file_queue[index].stimulation.id,
                        'site_panel': $scope.file_queue[index].site_panel.id,
                        'cytometer': $scope.current_cytometer.id,
                        'acquisition_date':
                                $scope.file_queue[index].acquisition_date.getFullYear().toString() +
                                "-" +
                                ($scope.file_queue[index].acquisition_date.getMonth() + 1) +
                                "-" +
                                $scope.file_queue[index].acquisition_date.getDate().toString()
                    },

                    file: $scope.file_queue[index].file,
                    fileFormDataName: 'sample_file'

                }).error(function(errors, status, xhr, request) {
                    if (Object.keys(errors).length > 0) {
                        $scope.file_queue[index].errors = [];

                        for (key in errors) {
                            $scope.file_queue[index].errors.push(
                                {
                                    'key': key,
                                    'value': errors[key]
                                }
                            );
                        }
                        $scope.$apply();
                    }
                }).then(function(response) {
                    $scope.file_queue[index].uploadResult.push(response.data);
                }, null, function(evt) {
                    $scope.file_queue[index].progress = parseInt(100.0 * evt.loaded / evt.total);
                });
            }

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

                $scope.opened = true;
            };

            $scope.dateOptions = {
                'year-format': "'yy'",
                'starting-day': 1
            };

            $scope.formats = ['dd-MMMM-yyyy', 'yyyy/MM/dd', 'shortDate'];
            $scope.format = $scope.formats[0];

        }
    ]
);

