app.controller(
    'PanelTemplateQueryController',
    ['$scope', 'ModelService', function ($scope, ModelService) {
        // everything but bead panels
        var PANEL_TYPES = ['FS', 'US', 'FM', 'IS'];

        // get panel templates
        $scope.sample_upload_model.panel_templates = ModelService.getPanelTemplates(
            {
                project: $scope.current_project.id,
                staining: PANEL_TYPES
            }
        );

        $scope.panelChanged = function () {
            ModelService.sitePanelsUpdated();
        };

        $scope.$on('site_panels:updated', function (evt, id) {
            var site_panel_query = {
                project: $scope.current_project.id,
                panel_type: PANEL_TYPES
            };

            if ($scope.sample_upload_model.current_panel_template) {
                site_panel_query.site = $scope.sample_upload_model.current_site.id;
            }

            if ($scope.sample_upload_model.current_panel_template) {
                site_panel_query.panel_template = $scope.sample_upload_model.current_panel_template.id;
            }

            $scope.sample_upload_model.site_panels = ModelService.getSitePanels(
                site_panel_query
            );
            $scope.sample_upload_model.site_panels.$promise.then(function (o) {
                $scope.evaluateParameterMatch();
            });
        });
    }
]);

app.controller(
    'CategorizationController',
    ['$scope', '$modal', 'ModelService', function ($scope, $modal, ModelService) {
        $scope.sample_upload_model.file_queue = [];
        $scope.sample_upload_model.site_panels = [];

        $scope.siteChanged = function () {
            $scope.$broadcast('siteChangedEvent');
            ModelService.sitePanelsUpdated();
        };

        $scope.$on('recheckSitePanels', function () {
            $scope.evaluateParameterMatch();
        });

        $scope.evaluateParameterMatch = function () {
            for (var i = 0; i < $scope.sample_upload_model.file_queue.length; i++) {
                // Reset the file's site panel
                $scope.sample_upload_model.file_queue[i].site_panel = null;

                for (var j = 0; j < $scope.sample_upload_model.site_panels.length; j++) {
                    if (file_matches_panel(i, $scope.sample_upload_model.site_panels[j])) {
                        $scope.sample_upload_model.file_queue[i].site_panel = $scope.sample_upload_model.site_panels[j];
                        break;
                    }
                }
            }
        };

        $scope.removeFromFileQueue = function(f) {
            $scope.sample_upload_model.file_queue.splice($scope.sample_upload_model.file_queue.indexOf(f), 1);
        };

        // Date picker stuff
        $scope.today = function() {
            $scope.dt = new Date();
        };
        $scope.today();

        $scope.clear = function () {
            $scope.dt = null;
        };

        $scope.open = function($event, f) {
            $event.preventDefault();
            $event.stopPropagation();

            var f_index = $scope.sample_upload_model.file_queue.indexOf(f);

            $scope.sample_upload_model.file_queue[f_index].datepicker_open = true;
        };

        $scope.dateOptions = {
            'year-format': "'yy'",
            'starting-day': 1,
            'show-weeks': false
        };

        $scope.formats = ['dd-MMMM-yyyy', 'yyyy/MM/dd', 'shortDate'];
        $scope.format = $scope.formats[0];

        function verifyCategories() {
            return $scope.sample_upload_model.current_cytometer &&
                $scope.sample_upload_model.current_panel_template &&
                $scope.sample_upload_model.current_subject &&
                $scope.sample_upload_model.current_visit &&
                $scope.sample_upload_model.current_stimulation &&
                $scope.sample_upload_model.current_specimen &&
                $scope.sample_upload_model.current_pretreatment &&
                $scope.sample_upload_model.current_storage;
        }

        // site panel matching
        function file_matches_panel(file_index, site_panel) {
            // first make sure the number of params is the same
            if ($scope.sample_upload_model.file_queue[file_index].channels.length != site_panel.parameters.length) {
                return false;
            }

            // iterate through site panel params, use channel number to
            // find the corresponding PnN and PnS fields in FCS object
            // channels property.
            // collect mis-matches to report them in errors array
            var mismatches = [];
            for (var i = 0; i < site_panel.parameters.length; i++) {
                var channel = $scope.sample_upload_model.file_queue[file_index].channels.filter(function(item) {
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

            return mismatches.length <= 0;
        }

        $scope.initSitePanel = function(f) {
            // a little confusing but we want to trigger the site panel creation
            // only when the user just selected the checkbox, so the selected
            // field will still be false for this case
            if (f.site_panel == null && f.selected == false) {
                // set global current sample
                ModelService.setCurrentSite($scope.sample_upload_model.current_site);
                ModelService.setCurrentSample(f);
                ModelService.setCurrentPanelTemplate($scope.sample_upload_model.current_panel_template);

                // launch site panel creation modal
                var modalInstance = $modal.open({
                    templateUrl: 'static/ng-app/partials/create_site_panel.html',
                    controller: ModalInstanceCtrl,
                    size: 'lg',
                    resolve: {
                        file: function() {
                            return f;
                        }
                    }
                });
            }
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
            for (var i = 0; i < $scope.sample_upload_model.file_queue.length; i++) {
                $scope.sample_upload_model.file_queue[i].selected = $scope.master_file_queue_checkbox;
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
                obj.matching_panels = [];

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
                        // Try to parse into JS Date
                        var date = new Date(non_paired_list[i+1]);
                        if (isNaN(date)) {
                            obj.acquisition_date = null;
                        } else {
                            obj.acquisition_date = date;
                        }
                    }

                    if (pnn_result) {
                        for (var j = 0; j < obj.channels.length; j++) {
                            if (obj.channels[j].channel == pnn_result[1]) {
                                index = j;
                                break;
                            }
                        }
                        if (index != null) {
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
                        if (index != null) {
                            obj.channels[j].pns = non_paired_list[i+1];
                        } else {
                            obj.channels.push(
                                {
                                    'channel': pns_result[1],
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
                    $scope.sample_upload_model.file_queue.push(obj);
                    // loop over site panels to find and set match
                    if ($scope.sample_upload_model.site_panels.length > 0) {
                        $scope.sample_upload_model.site_panels.forEach(function (panel) {
                            var obj_index = $scope.sample_upload_model.file_queue.length - 1;

                            if (file_matches_panel(obj_index, panel)) {
                                obj.site_panel = panel;
                            }
                        });
                    }
                });
            });

            var blob = obj.file.slice(obj.text_begin, obj.text_end);
            reader.readAsBinaryString(blob);
        }

        $scope.onFileSelect = function($files) {
            for (var i = 0; i < $files.length; i++) {
                setupReader({
                    filename: $files[i].name,
                    file: $files[i],
                    datepicker_open: false,
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

        $scope.addSelectedToUploadQueue = function() {
            for (var i = 0; i < $scope.sample_upload_model.file_queue.length; i++) {
                if ($scope.sample_upload_model.file_queue[i].selected) {
                    // ensure all the category fields have data
                    if (! verifyCategories() || ! $scope.sample_upload_model.file_queue[i].acquisition_date) {
                        return false;
                    }

                    // verify site panel matches TODO: is this necessary
                    if (!file_matches_panel(i, $scope.sample_upload_model.file_queue[i].site_panel)) {
                        continue;
                    }

                    // populate the file object properties
                    $scope.sample_upload_model.file_queue[i].cytometer = $scope.sample_upload_model.current_cytometer;
                    $scope.sample_upload_model.file_queue[i].subject = $scope.sample_upload_model.current_subject;
                    $scope.sample_upload_model.file_queue[i].visit_type = $scope.sample_upload_model.current_visit;
                    $scope.sample_upload_model.file_queue[i].stimulation = $scope.sample_upload_model.current_stimulation;
                    $scope.sample_upload_model.file_queue[i].specimen = $scope.sample_upload_model.current_specimen;
                    $scope.sample_upload_model.file_queue[i].pretreatment = $scope.sample_upload_model.current_pretreatment;
                    $scope.sample_upload_model.file_queue[i].storage = $scope.sample_upload_model.current_storage;

                    // Add to upload queue
                    $scope.sample_upload_model.upload_queue.push($scope.sample_upload_model.file_queue[i]);

                    // Remove from file queue
                    $scope.sample_upload_model.file_queue.splice(i, 1);
                    i--;
                }
            }
        };
    }
]);

app.controller(
    'UploadQueueController',
    ['$scope', '$rootScope', '$upload', '$modal', function ($scope, $rootScope, $upload, $modal) {
        $scope.sample_upload_model.upload_queue = [];

        $scope.clearUploaded = function() {
            for (var i = 0; i < $scope.sample_upload_model.upload_queue.length; i++) {
                if ($scope.sample_upload_model.upload_queue[i].uploaded) {
                    $scope.sample_upload_model.upload_queue.splice(i, 1);
                    i--;
                }
            }
        };

        $scope.clearSelected = function() {
            for (var i = 0; i < $scope.sample_upload_model.upload_queue.length; i++) {
                if ($scope.sample_upload_model.upload_queue[i].selected && ! $scope.sample_upload_model.upload_queue[i].uploading) {
                    $scope.sample_upload_model.upload_queue.splice(i, 1);
                    i--;
                }
            }
        };

        $scope.toggleAllUploadQueue = function () {
            for (var i = 0; i < $scope.sample_upload_model.upload_queue.length; i++) {
                // only select the non-uploaded files
                if (! $scope.sample_upload_model.upload_queue[i].uploaded) {
                    $scope.sample_upload_model.upload_queue[i].selected = $scope.master_upload_queue_checkbox;
                }
            }
        };
        
        $scope.recategorizeFile = function(f) {

            // clear the file object properties
            f.cytometer = null;
            f.subject = null;
            f.visit_type = null;
            f.stimulation = null;
            f.specimen = null;
            f.pretreatment = null;
            f.storage = null;

            // reset site panel and de-select. this is necessary b/c a different
            // panel template than this site panel's parent may now be chosen
            // and we need to de-select b/c the site panel matching and assignment
            // occurs on checking the checkbox in the file queue
            f.site_panel = null;
            f.selected = false;

            // Add back to file queue
            $scope.sample_upload_model.file_queue.push(f);

            // Remove from upload queue
            $scope.sample_upload_model.upload_queue.splice($scope.sample_upload_model.upload_queue.indexOf(f), 1);

            // re-check site panel matches
            $rootScope.$broadcast('recheckSitePanels');

        };

        $scope.uploadSelected = function() {
            // first iterate through all the selected and mark as uploading
            // we do this so all the selected files get marked, since
            // the uploads may take a while and we don't want the user
            // interacting with the ones we are trying to upload
            $scope.sample_upload_model.upload_queue.forEach(function (obj) {
                if (obj.selected && !obj.uploaded) {
                    obj.uploading = true;
                } else {
                    obj.uploading = false;
                }
            });
            // now actually call upload for all the marked files
            for (var i = 0; i < $scope.sample_upload_model.upload_queue.length; i++) {
                if ($scope.sample_upload_model.upload_queue[i].uploading) {
                    upload(i);
                }
            }
        };

        function upload(index) {
            $scope.sample_upload_model.upload_queue[index].progress = 0;
            $scope.sample_upload_model.upload_queue[index].errors = null;

            if (! $scope.sample_upload_model.upload_queue[index].subject ||
                ! $scope.sample_upload_model.upload_queue[index].visit_type ||
                ! $scope.sample_upload_model.upload_queue[index].specimen ||
                ! $scope.sample_upload_model.upload_queue[index].pretreatment ||
                ! $scope.sample_upload_model.upload_queue[index].storage ||
                ! $scope.sample_upload_model.upload_queue[index].stimulation ||
                ! $scope.sample_upload_model.upload_queue[index].site_panel ||
                ! $scope.sample_upload_model.upload_queue[index].cytometer ||
                ! $scope.sample_upload_model.upload_queue[index].acquisition_date)
            {
                $scope.sample_upload_model.upload_queue[index].errors = [];
                $scope.sample_upload_model.upload_queue[index].errors.push(
                    {
                        'key': 'Missing fields',
                        'value': 'Please select all fields for the FCS sample.'
                    }
                );
                // reset uploading status else checkbox stays disabled
                $scope.sample_upload_model.upload_queue[index].uploading = false;
                return;
            }

            $scope.sample_upload_model.upload_queue[index].upload = $upload.upload({
                url : '/api/repository/samples/add/',
                method: 'POST',

                // FCS sample's REST API model fields here
                data : {
                    'subject': $scope.sample_upload_model.upload_queue[index].subject.id,
                    'visit': $scope.sample_upload_model.upload_queue[index].visit_type.id,
                    'specimen': $scope.sample_upload_model.upload_queue[index].specimen.id,
                    'pretreatment': $scope.sample_upload_model.upload_queue[index].pretreatment.name,
                    'storage': $scope.sample_upload_model.upload_queue[index].storage.name,
                    'stimulation': $scope.sample_upload_model.upload_queue[index].stimulation.id,
                    'site_panel': $scope.sample_upload_model.upload_queue[index].site_panel.id,
                    'cytometer': $scope.sample_upload_model.upload_queue[index].cytometer.id,
                    'acquisition_date':
                            $scope.sample_upload_model.upload_queue[index].acquisition_date.getFullYear().toString() +
                            "-" +
                            ($scope.sample_upload_model.upload_queue[index].acquisition_date.getMonth() + 1) +
                            "-" +
                            $scope.sample_upload_model.upload_queue[index].acquisition_date.getDate().toString()
                },

                file: $scope.sample_upload_model.upload_queue[index].file,
                fileFormDataName: 'sample_file'
            }).progress(function(evt) {
                $scope.sample_upload_model.upload_queue[index].progress = parseInt(100.0 * evt.loaded / evt.total);
            }).success(function(data, status, headers, config) {
                $scope.sample_upload_model.upload_queue[index].uploaded = true;
                $scope.sample_upload_model.upload_queue[index].selected = false;
            }).error(function(error) {
                if (Object.keys(error).length > 0) {
                    $scope.sample_upload_model.upload_queue[index].errors = [];

                    for (var key in error) {
                        $scope.sample_upload_model.upload_queue[index].errors.push(
                            {
                                'key': key,
                                'value': error[key]
                            }
                        );
                    }
                }
                // reset uploading status else checkbox stays disabled
                $scope.sample_upload_model.upload_queue[index].uploading = false;
            });
        }

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
    }
]);