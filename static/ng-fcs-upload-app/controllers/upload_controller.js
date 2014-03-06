/**
 * Created by swhite on 2/25/14.
 */
app.controller(
    'UploadController',
    [
        '$scope',
        '$http',
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
        function ($scope, $http, $timeout, $upload, Project, Site, Specimen, Cytometer, Pretreatment, Storage, Stimulation, VisitType, Subject, SitePanel) {
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
                $scope.site_panels = SitePanel.query({project: $scope.current_project.id});
            };
            
            $scope.acquisitionDateChanged = function () {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    if ($scope.file_queue[i].selected) {
                        $scope.file_queue[i].acquisition_date = $scope.current_acquisition_date;
                    }
                }
                $scope.current_acquisition_date = null;
            };

            $scope.sitePanelChanged = function () {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    if ($scope.file_queue[i].selected) {
                        $scope.file_queue[i].site_panel = $scope.current_site_panel;
                    }
                }
                $scope.current_site_panel = null;
            };
            
            $scope.subjectChanged = function () {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    if ($scope.file_queue[i].selected) {
                        $scope.file_queue[i].subject = $scope.current_subject;
                    }
                }
                $scope.current_subject = null;
            };
            
            $scope.visitTypeChanged = function () {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    if ($scope.file_queue[i].selected) {
                        $scope.file_queue[i].visit_type = $scope.current_visit_type;
                    }
                }
                $scope.current_visit_type = null;
            };
            
            $scope.stimulationChanged = function () {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    if ($scope.file_queue[i].selected) {
                        $scope.file_queue[i].stimulation = $scope.current_stimulation;
                    }
                }
                $scope.current_stimulation = null;
            };
            
            $scope.specimenChanged = function () {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    if ($scope.file_queue[i].selected) {
                        $scope.file_queue[i].specimen = $scope.current_specimen;
                    }
                }
                $scope.current_specimen = null;
            };
            
            $scope.pretreatmentChanged = function () {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    if ($scope.file_queue[i].selected) {
                        $scope.file_queue[i].pretreatment = $scope.current_pretreatment;
                    }
                }
                $scope.current_pretreatment = null;
            };
            
            $scope.storageChanged = function () {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    if ($scope.file_queue[i].selected) {
                        $scope.file_queue[i].storage = $scope.current_storage;
                    }
                }
                $scope.current_storage = null;
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
                        selected: false
                    });
                }
            };

            $scope.start = function(index) {
                $scope.progress[index] = 0;

                $scope.upload[index] = $upload.upload({
                    url : 'upload',
                    method: 'POST',
                    headers: {'myHeaderKey': 'myHeaderVal'},

                    // put the sample's model data here
                    data : {
                        myModel : $scope.myModel
                    },

                    file: $scope.selectedFiles[index],

                    // TODO: change the file name
                    fileFormDataName: 'myFile'
                }).then(function(response) {
                    $scope.uploadResult.push(response.data);
                }, null, function(evt) {
                    $scope.progress[index] = parseInt(100.0 * evt.loaded / evt.total);
                });

            };

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

