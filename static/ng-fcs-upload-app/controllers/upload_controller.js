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
            $scope.upload_queue = [];

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
                $scope.site_panels = SitePanel.query(
                    {
                        project_panel__project: $scope.current_project.id,
                        site: $scope.current_site.id
                    }
                );
            };

            $scope.evaluateParameterMatch = function () {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    file_matches_panel(i, $scope.current_site_panel);
                }
            };

            $scope.removeFromFileQueue = function(f) {
                $scope.file_queue.splice($scope.file_queue.indexOf(f), 1);
            };
            
            function verifyCategories() {
                return $scope.current_cytometer &&
                    $scope.current_acquisition_date &&
                    $scope.current_site_panel &&
                    $scope.current_subject &&
                    $scope.current_visit &&
                    $scope.current_stimulation &&
                    $scope.current_specimen &&
                    $scope.current_pretreatment &&
                    $scope.current_storage;
            }
            
            $scope.addSelectedToUploadQueue = function() {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    if ($scope.file_queue[i].selected) {
                        // ensure all the category fields have data
                        if (! verifyCategories()) {
                            return false;
                        }

                        // verify panel matches
                        if (!file_matches_panel(i, $scope.current_site_panel)) {
                            continue;
                        }

                        // populate the file object properties
                        $scope.file_queue[i].acquisition_date = $scope.current_acquisition_date;
                        $scope.file_queue[i].site_panel = $scope.current_site_panel;
                        $scope.file_queue[i].cytometer = $scope.current_cytometer;
                        $scope.file_queue[i].subject = $scope.current_subject;
                        $scope.file_queue[i].visit_type = $scope.current_visit;
                        $scope.file_queue[i].stimulation = $scope.current_stimulation;
                        $scope.file_queue[i].specimen = $scope.current_specimen;
                        $scope.file_queue[i].pretreatment = $scope.current_pretreatment;
                        $scope.file_queue[i].storage = $scope.current_storage;
                        
                        // Add to upload queue
                        $scope.upload_queue.push($scope.file_queue[i]);
                        
                        // Remove from file queue
                        $scope.file_queue.splice(i, 1);
                        i--;
                    }
                }
            };

            $scope.clearUploaded = function() {
                for (var i = 0; i < $scope.upload_queue.length; i++) {
                    if ($scope.upload_queue[i].uploaded) {
                        $scope.upload_queue.splice(i, 1);
                        i--;
                    }
                }
            };

            $scope.clearSelected = function() {
                for (var i = 0; i < $scope.upload_queue.length; i++) {
                    if ($scope.upload_queue[i].selected && ! $scope.upload_queue[i].uploading) {
                        $scope.upload_queue.splice(i, 1);
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

            $scope.toggleAllFileQueue = function () {
                for (var i = 0; i < $scope.file_queue.length; i++) {
                    $scope.file_queue[i].selected = $scope.master_file_queue_checkbox;
                }
            };

            $scope.toggleAllUploadQueue = function () {
                for (var i = 0; i < $scope.upload_queue.length; i++) {
                    // only select the non-uploaded files
                    if (! $scope.upload_queue[i].uploaded) {
                        $scope.upload_queue[i].selected = $scope.master_upload_queue_checkbox;
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
                    var date_pattern = /^\$DATE$/i;

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
                        var date_result = date_pattern.exec(non_paired_list[i]);

                        var index = null;

                        if (date_result) {
                            obj.date = non_paired_list[i+1];
                        }

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
                        date: "",
                        metadata: {},
                        selected: false,
                        progress: 0,
                        uploading: false,
                        uploaded: false,
                        acquisition_date: null,
                        site_panel: null,
                        cytometer: null,
                        subject: null,
                        visit_type: null,
                        stimulation: null,
                        specimen: null,
                        pretreatment: null,
                        storage: null
                    });
                }
            };

            $scope.uploadSelected = function() {
                // first iterate through all the selected and mark as uploading
                // we do this so all the selected files get marked, since
                // the uploads may take a while and we don't want the user
                // interacting with the ones we are trying to upload
                for (var i = 0; i < $scope.upload_queue.length; i++) {
                    if ($scope.upload_queue[i].selected) {
                        $scope.upload_queue[i].uploading = true;
                    }
                }
                // now actually call upload for all the marked files
                for (var i = 0; i < $scope.upload_queue.length; i++) {
                    if ($scope.upload_queue[i].uploading) {
                        upload(i);
                    }
                }
            };

            function upload(index) {
                $scope.upload_queue[index].progress = 0;
                $scope.upload_queue[index].errors = null;

                if (! $scope.upload_queue[index].subject ||
                    ! $scope.upload_queue[index].visit_type ||
                    ! $scope.upload_queue[index].specimen ||
                    ! $scope.upload_queue[index].pretreatment ||
                    ! $scope.upload_queue[index].storage ||
                    ! $scope.upload_queue[index].stimulation ||
                    ! $scope.upload_queue[index].site_panel ||
                    ! $scope.upload_queue[index].cytometer ||
                    ! $scope.upload_queue[index].acquisition_date)
                {
                    $scope.upload_queue[index].errors = [];
                    $scope.upload_queue[index].errors.push(
                        {
                            'key': 'Missing fields',
                            'value': 'Please select all fields for the FCS sample.'
                        }
                    );
                    // reset uploading status else checkbox stays disabled
                    $scope.upload_queue[index].uploading = false;
                    return;
                }

                $scope.upload_queue[index].upload = $upload.upload({
                    url : '/api/repository/samples/add/',
                    method: 'POST',

                    // FCS sample's REST API model fields here
                    data : {
                        'subject': $scope.upload_queue[index].subject.id,
                        'visit': $scope.upload_queue[index].visit_type.id,
                        'specimen': $scope.upload_queue[index].specimen.id,
                        'pretreatment': $scope.upload_queue[index].pretreatment.name,
                        'storage': $scope.upload_queue[index].storage.name,
                        'stimulation': $scope.upload_queue[index].stimulation.id,
                        'site_panel': $scope.upload_queue[index].site_panel.id,
                        'cytometer': $scope.upload_queue[index].cytometer.id,
                        'acquisition_date':
                                $scope.upload_queue[index].acquisition_date.getFullYear().toString() +
                                "-" +
                                ($scope.upload_queue[index].acquisition_date.getMonth() + 1) +
                                "-" +
                                $scope.upload_queue[index].acquisition_date.getDate().toString()
                    },

                    file: $scope.upload_queue[index].file,
                    fileFormDataName: 'sample_file'
                }).progress(function(evt) {
                    $scope.upload_queue[index].progress = parseInt(100.0 * evt.loaded / evt.total);
                }).success(function(data, status, headers, config) {
                    $scope.upload_queue[index].uploaded = true;
                    $scope.upload_queue[index].selected = false;
                }).error(function(error) {
                    if (Object.keys(error).length > 0) {
                        $scope.upload_queue[index].errors = [];

                        for (var key in error) {
                            $scope.upload_queue[index].errors.push(
                                {
                                    'key': key,
                                    'value': error[key]
                                }
                            );
                        }
                    }
                    // reset uploading status else checkbox stays disabled
                    $scope.upload_queue[index].uploading = false;
                });
            }

            $scope.open_site_panel_mismatch_modal = function (f) {

                var modalInstance = $modal.open({
                    templateUrl: 'sitePanelMismatchModal.html',
                    controller: ModalInstanceCtrl,
                    resolve: {
                        file: function() {
                            return f;
                        }
                    }
                });
            };

            $scope.open_error_modal = function (f) {

                var modalInstance = $modal.open({
                    templateUrl: 'myModalContent.html',
                    controller: ModalInstanceCtrl,
                    resolve: {
                        file: function() {
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
                        file: function() {
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
                        file: function() {
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

var ModalInstanceCtrl = function ($scope, $modalInstance, file) {
    $scope.file = file;
    $scope.ok = function () {
        $modalInstance.close();
    };

};