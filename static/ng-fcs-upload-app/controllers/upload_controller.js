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

            // file reader stuff
            $scope.fileReaderSupported = window.FileReader != null;
            $scope.hasUploader = function(index) {
                return $scope.upload[index] != null;
            };
            $scope.abort = function(index) {
                $scope.upload[index].abort();
                $scope.upload[index] = null;
            };

            function setupReader(queue_index) {
                var reader = new FileReader();
                reader.addEventListener("loadend", function(evt) {
                    var preheader = evt.target.result;

                    // TODO: Check 1st 6 bytes to make sure this is an FCS file

                    // The following uses the FCS standard offset definitions
                    $scope.file_queue[queue_index].text_begin = parseInt(preheader.substr(10, 8));
                    $scope.file_queue[queue_index].text_end = parseInt(preheader.substr(18, 8));
                    $scope.file_queue[queue_index].data_begin = parseInt(preheader.substr(26, 8));
                    $scope.file_queue[queue_index].data_end = parseInt(preheader.substr(34, 8));
                    parseFcsText(queue_index);
                });
                var blob = $scope.file_queue[queue_index].file.slice(0, 58);
                reader.readAsBinaryString(blob);
            }

            function parseFcsText(queue_index) {
                var reader = new FileReader();
                reader.addEventListener("loadend", function(evt) {
                    var delimiter = evt.target.result[0];
                    var non_paired_list = evt.target.result.split(delimiter);
                    var metadata = [];

                    // first match will be empty string since the FCS TEXT
                    // segment starts with the delimiter, so we'll start at
                    // the 2nd index
                    for (var i = 1; i < non_paired_list.length; i+=2) {
                        metadata.push(
                            {
                                key: non_paired_list[i],
                                value: non_paired_list[i+1]
                            }
                        );
                    }

                    // Using $apply here to trigger template update
                    $scope.$apply(function () {
                        $scope.file_queue[queue_index].metadata = metadata;
                    });
                });

                var blob = $scope.file_queue[queue_index].file.slice(
                    $scope.file_queue[queue_index].text_begin,
                    $scope.file_queue[queue_index].text_end
                );
                reader.readAsBinaryString(blob);
            }

            $scope.onFileSelect = function($files) {
                $scope.file_queue = [];

                for (var i = 0; i < $files.length; i++) {
                    $scope.file_queue.push({
                        filename: $files[i].name,
                        file: $files[i],
                        metadata: {}
                    });

                    setupReader(i);
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

            }

        }
    ]
);

