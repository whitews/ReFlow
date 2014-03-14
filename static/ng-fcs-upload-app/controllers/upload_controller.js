/**
 * Created by swhite on 2/25/14.
 */
app.controller(
    'UploadController',
    [
        '$scope',
        '$timeout',
        '$upload',
        '$modal',
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
        function ($scope, $timeout, $upload, $modal, Project, Site, Specimen, Cytometer, Pretreatment, Storage, Stimulation, VisitType, Subject, SitePanel) {
            $scope.projects = Project.query();
            $scope.specimens = Specimen.query();
            $scope.pretreatments = Pretreatment.query();
            $scope.storages = Storage.query();

            $scope.file_queue = [];

            $scope.projectChanged = function () {
                $scope.sites = Site.query({project: $scope.current_project.id});
                $scope.current_site = null;
                $scope.current_cytometer = null;
                $scope.stimulations = Stimulation.query({project: $scope.current_project.id});
                $scope.visit_types = VisitType.query({project: $scope.current_project.id});
                $scope.subjects = Subject.query({project: $scope.current_project.id});

                // Clear any project related choices from non-uploaded files in queue
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    if (! $scope.file_queue[i].uploaded) {
                        $scope.file_queue[i].site_panel = null;
                        $scope.file_queue[i].subject = null;
                        $scope.file_queue[i].visit_type = null;
                        $scope.file_queue[i].stimulation = null;
                    }
                }
            };

            $scope.siteChanged = function () {
                $scope.cytometers = Cytometer.query({site: $scope.current_site.id});
                $scope.current_cytometer = null;
                $scope.site_panels = SitePanel.query(
                    {
                        project_panel__project: $scope.current_project.id,
                        site: $scope.current_site.id
                    }
                );

                // Clear any site related choices from non-uploaded files in queue
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    if (! $scope.file_queue[i].uploaded) {
                        $scope.file_queue[i].site_panel = null;
                    }
                }
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
                        if (file_matches_panel(i, selected)) {
                            $scope.file_queue[i].site_panel = selected;
                        }
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

            $scope.clearUploaded = function() {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    if ($scope.file_queue[i].uploaded) {
                        $scope.file_queue.splice(i, 1);
                        i--;
                    }
                }
            };

            $scope.clearSelected = function() {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    if ($scope.file_queue[i].selected) {
                        $scope.file_queue.splice(i, 1);
                        i--;
                    }
                }
            };

            // site panel matching
            function file_matches_panel(file_index, site_panel) {
                // first make sure the number of params is the same
                if ($scope.file_queue[file_index].channels.length != site_panel.parameters.length) {
                    $scope.file_queue[file_index].errors = [];
                    $scope.file_queue[file_index].errors.push(
                        {
                            'key': 'Incompatible site panel',
                            'value': "The number of parameters in chosen site panel and FCS file are not equal."
                        }
                    );
                    return false;
                }

                // iterate through site panel params, use channel number to
                // find the corresponding PnN and PnS fields in FCS object
                // channels property.
                // collect mis-matches to report them in errors array
                var mismatches = [];
                for (var i = 0; i < site_panel.parameters.length; i++) {
                    var channel = $scope.file_queue[file_index].channels.filter(function(item) {
                        return (item.channel == site_panel.parameters[i].fcs_number);
                    });

                    if (channel.length > 0) {
                        if (site_panel.parameters[i].fcs_text != channel[0].pnn) {
                            mismatches.push(
                                "PnN mismatch in channel " +
                                site_panel.parameters[i].fcs_number +
                                ": expected " +
                                site_panel.parameters[i].fcs_text +
                                ", file has " +
                                channel[0].pnn);
                        }

                        if (site_panel.parameters[i].fcs_opt_text != channel[0].pns) {
                            mismatches.push(
                                "PnS mismatch in channel " +
                                site_panel.parameters[i].fcs_number +
                                ": expected " +
                                site_panel.parameters[i].fcs_opt_text +
                                ", file has " +
                                channel[0].pns);
                        }
                    }
                }

                if (mismatches.length > 0) {
                    $scope.file_queue[file_index].errors = [];
                    $scope.file_queue[file_index].errors.push(
                        {
                            'key': 'Incompatible site panel',
                            'value': mismatches.join('<br />')
                        }
                    );
                    return false;
                }
                return true;
            }

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
                    // only select the non-uploaded filess
                    if (! $scope.file_queue[i].uploaded) {
                        $scope.file_queue[i].selected = $scope.master_checkbox;
                    }
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
                    obj.channels = [];

                    var pnn_pattern = /\$P(\d+)N/i;
                    var pns_pattern = /\$P(\d+)S/i;

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

                        var pnn_result = pnn_pattern.exec(non_paired_list[i]);
                        var pns_result = pns_pattern.exec(non_paired_list[i]);

                        var index = null;

                        if (pnn_result) {
                            for (var j = 0; j < obj.channels.length; j++) {
                                if (obj.channels[j].channel == pnn_result[1]) {
                                    index = j;
                                    break;
                                }
                            }
                            if (index) {
                                obj.channels[j].pnn = non_paired_list[i+1];
                            } else {
                                obj.channels.push(
                                    {
                                        'channel': pnn_result[1],
                                        'pnn': non_paired_list[i+1]
                                    }
                                );
                            }
                        }

                        if (pns_result) {
                            for (var j = 0; j < obj.channels.length; j++) {
                                if (obj.channels[j].channel == pns_result[1]) {
                                    index = j;
                                    break;
                                }
                            }
                            if (index) {
                                obj.channels[j].pns = non_paired_list[i+1];
                            } else {
                                obj.channels.push(
                                    {
                                        'channel': pnn_result[1],
                                        'pns': non_paired_list[i+1]
                                    }
                                );
                            }
                        }
                    }

                    // Now check our channels for missing PnS fields, since
                    // they are optional in the FCS file. Add empty strings,
                    // where they are missing (so our panel matching works)
                    for (var j = 0; j < obj.channels.length; j++) {
                        if (! obj.channels[j].pns) {
                            obj.channels[j].pns = "";
                        }
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

                $scope.current_acquisition_date = "";

                for (var i = 0; i < $files.length; i++) {
                    setupReader({
                        filename: $files[i].name,
                        file: $files[i],
                        metadata: {},
                        selected: false,
                        progress: 0
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
                $scope.file_queue[index].errors = null;

                if (! $scope.file_queue[index].subject ||
                    ! $scope.file_queue[index].visit_type ||
                    ! $scope.file_queue[index].specimen ||
                    ! $scope.file_queue[index].pretreatment ||
                    ! $scope.file_queue[index].storage ||
                    ! $scope.file_queue[index].stimulation ||
                    ! $scope.file_queue[index].site_panel ||
                    ! $scope.current_cytometer ||
                    ! $scope.file_queue[index].acquisition_date)
                {
                    $scope.file_queue[index].errors = [];
                    $scope.file_queue[index].errors.push(
                        {
                            'key': 'Missing fields',
                            'value': 'Please select all fields for the FCS sample.'
                        }
                    );
                    return;
                }

                $scope.file_queue[index].upload = $upload.upload({
                    url : '/api/repository/samples/add/',
                    method: 'POST',

                    // FCS sample's REST API model fields here
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
                }).progress(function(evt) {
                    $scope.file_queue[index].progress = parseInt(100.0 * evt.loaded / evt.total);
                }).success(function(data, status, headers, config) {
                    $scope.file_queue[index].uploaded = true;
                    $scope.file_queue[index].selected = false;
                }).error(function(error) {
                    if (Object.keys(error).length > 0) {
                        $scope.file_queue[index].errors = [];

                        for (var key in error) {
                            $scope.file_queue[index].errors.push(
                                {
                                    'key': key,
                                    'value': error[key]
                                }
                            );
                        }
                    }
                });
            }

            $scope.open_error_modal = function (f) {

                var modalInstance = $modal.open({
                    templateUrl: 'myModalContent.html',
                    controller: ModalInstanceCtrl,
                    resolve: {
                        upload_file: function() {
                            return f;
                        }
                    }
                });
            };

            $scope.open_metadata_modal = function (f) {

                var modalInstance = $modal.open({
                    templateUrl: 'metadata_content.html',
                    controller: ModalInstanceCtrl,
                    resolve: {
                        upload_file: function() {
                            return f;
                        }
                    }
                });
            };

            $scope.open_channels_modal = function (f) {

                var modalInstance = $modal.open({
                    templateUrl: 'channels_content.html',
                    controller: ModalInstanceCtrl,
                    resolve: {
                        upload_file: function() {
                            return f;
                        }
                    }
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

var ModalInstanceCtrl = function ($scope, $modalInstance, upload_file) {
    $scope.upload_file = upload_file;
    $scope.ok = function () {
        $modalInstance.close();
    };

};