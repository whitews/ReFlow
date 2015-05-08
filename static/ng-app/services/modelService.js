var service = angular.module('ReFlowApp');

service.factory('ModelService', function(
        $rootScope,
        $http,
        User,
        CurrentUser,
        UserPermissions,
        Marker,
        Fluorochrome,
        Specimen,
        Pretreatment,
        Storage,
        StainingType,
        Worker,
        Project,
        ProjectUsers,
        SubjectGroup,
        Subject,
        VisitType,
        CellSubsetLabel,
        Stimulation,
        PanelTemplate,
        PanelVariant,
        Site,
        Cytometer,
        SitePanel,
        Sample,
        BeadSample,
        SampleMetadata,
        Compensation,
        ParameterFunction,
        ParameterValueType,
        ProcessRequest,
        ProcessRequestStage2,
        ProcessRequestInput,
        SubprocessImplementation,
        SubprocessInput,
        SampleCollection,
        SampleCollectionMember,
        SampleCluster,
        ClusterLabel) {
    var service = {};

    // The following section is for storing/retrieving "global" variables
    // that are needed across various controllers
    service.user = CurrentUser.get();
    
    service.setCurrentSite = function (value) {
        this.current_site = value;
        $rootScope.$broadcast('siteChanged');
    };
    service.getCurrentSite = function () {
        return this.current_site;
    };
    service.current_site = null;
    service.current_sample = null;
    service.current_panel_template = null;
    // End "global" variables

    // CurrentUser services
    service.isUser = function (username) {
        return CurrentUser.is_user(
            {
                'username': username
            }
        );
    };
    
    // UserPermission services
    service.userPermissionsUpdated = function () {
        $rootScope.$broadcast('user_permissions:updated');
    };
    service.getUserPermissions = function(model, pk, username) {
        return UserPermissions.query(
            {
                'model': model,
                'object_pk': pk,
                'username': username
            }
        );
    };
    service.createUserPermission = function(model, pk, username, permission) {
        return UserPermissions.save(
            {
                'model': model,
                'object_pk': pk,
                'username': username,
                'permission_codename': permission
            }
        );
    };
    service.destroyUserPermission = function (instance) {
        return UserPermissions.delete({id: instance.id });
    };

    // Specimen services
    service.specimensUpdated = function () {
        $rootScope.$broadcast('specimens:updated');
    };
    service.getSpecimens = function() {
        return Specimen.query({});
    };
    service.createUpdateSpecimen = function(instance) {
        if (instance.id) {
            return Specimen.update(
                {id: instance.id },
                instance
            );
        } else {
            return Specimen.save(instance);
        }
    };
    service.destroySpecimen = function (instance) {
        return Specimen.delete({id: instance.id });
    };

    // Parameter Function services
    service.getParameterFunctions = function() {
        return ParameterFunction.query({});
    };

    // Parameter Value Type services
    service.getParameterValueTypes = function() {
        return ParameterValueType.query({});
    };
    
    // ReFlow User services (not object-level permissions)
    service.usersUpdated = function () {
        $rootScope.$broadcast('users:updated');
    };
    service.getUsers = function() {
        return User.query({});
    };
    service.createUpdateUser = function(instance) {
        if (instance.id) {
            return User.update(
                {id: instance.id },
                instance
            );
        } else {
            return User.save(instance);
        }
    };
    service.destroyUser = function (instance) {
        return User.delete({id: instance.id });
    };
    service.changeUserPassword = function(user_id, current_password, new_password) {
        return User.change_password(
            {
                user_id: user_id,
                current_password: current_password,
                new_password: new_password
            }
        );
    };

    // Worker services
    service.workersUpdated = function () {
        $rootScope.$broadcast('workers:updated');
    };
    service.getWorkers = function() {
        return Worker.query({});
    };
    service.createUpdateWorker = function(instance) {
        if (instance.id) {
            return Worker.update(
                {id: instance.id },
                instance
            );
        } else {
            return Worker.save(instance);
        }
    };
    service.destroyWorker = function (instance) {
        return Worker.delete({id: instance.id });
    };

    // Pretreatment services
    service.getPretreatments = function() {
        return Pretreatment.query({});
    };

    // Storage services
    service.getStorages = function() {
        return Storage.query({});
    };

    // StainingType services
    service.getStainingTypes = function() {
        return StainingType.query({});
    };

    // Project services
    service.getProjects = function() {
        return Project.query({});
    };
    service.setCurrentProjectById = function(id) {
        service.current_project = Project.get({'id':id});
        service.current_project.$promise.then(function(p) {
            p.permissions = {
                'can_view_project': false,
                'can_add_data': false,
                'can_modify_project': false,
                'can_process_data': false,
                'can_manage_users': false
            };
            p.getUserPermissions().$promise.then(function (result) {

                if (result.permissions.indexOf('view_project_data') != -1) {
                    p.permissions.can_view_project = true;
                }
                if (result.permissions.indexOf('add_project_data') != -1) {
                    p.permissions.can_add_data = true;
                }
                if (result.permissions.indexOf('modify_project_data') != -1) {
                    p.permissions.can_modify_project = true;
                }
                if (result.permissions.indexOf('submit_process_requests') != -1) {
                    p.permissions.can_process_data = true;
                }
                if (result.permissions.indexOf('manage_project_users') != -1) {
                    p.permissions.can_manage_users = true;
                }

                $rootScope.$broadcast('current_project:updated');
            });
        }, function() {
            $rootScope.$broadcast('current_project:invalid');
        });
    };
    service.projectsUpdated = function () {
        $rootScope.$broadcast('projects:updated');
    };
    service.createUpdateProject = function(instance) {
        if (instance.id) {
            return Project.update(
                {id: instance.id },
                instance
            );
        } else {
            return Project.save(instance);
        }
    };
    service.destroyProject = function (instance) {
        return Project.delete({id: instance.id });
    };

    // Project User services
    service.getProjectUsers = function(project_id) {
        return ProjectUsers.get(
            {
                'id': project_id
            }
        );
    };

    // Marker services
    service.markersUpdated = function () {
        $rootScope.$broadcast('markers:updated');
    };
    service.getMarkers = function(project_id) {
        return Marker.query(
            {
                'project': project_id
            }
        );
    };
    service.createUpdateMarker = function(instance) {
        if (instance.id) {
            return Marker.update(
                {id: instance.id },
                instance
            );
        } else {
            return Marker.save(instance);
        }
    };
    service.destroyMarker = function (instance) {
        return Marker.delete({id: instance.id });
    };

    // Fluorochrome services
    service.fluorochromesUpdated = function () {
        $rootScope.$broadcast('fluorochromes:updated');
    };
    service.getFluorochromes = function(project_id) {
        return Fluorochrome.query(
            {
                'project': project_id
            }
        );
    };
    service.createUpdateFluorochrome = function(instance) {
        if (instance.id) {
            return Fluorochrome.update(
                {id: instance.id },
                instance
            );
        } else {
            return Fluorochrome.save(instance);
        }
    };
    service.destroyFluorochrome = function (instance) {
        return Fluorochrome.delete({id: instance.id });
    };

    // Subject Group services
    service.subjectGroupsUpdated = function () {
        $rootScope.$broadcast('subject_groups:updated');
    };
    service.getSubjectGroups = function(project_id) {
        return SubjectGroup.query(
            {
                'project': project_id
            }
        );
    };
    service.createUpdateSubjectGroup = function(instance) {
        if (instance.id) {
            return SubjectGroup.update(
                {id: instance.id },
                instance
            );
        } else {
            return SubjectGroup.save(instance);
        }
    };
    service.destroySubjectGroup = function (instance) {
        return SubjectGroup.delete({id: instance.id });
    };
    
    // Subject services
    service.subjectsUpdated = function () {
        $rootScope.$broadcast('subjects:updated');
    };
    service.getSubjects = function(project_id) {
        return Subject.query(
            {
                'project': project_id
            }
        );
    };
    service.createUpdateSubject = function(instance) {
        if (instance.id) {
            return Subject.update(
                {id: instance.id },
                instance
            );
        } else {
            return Subject.save(instance);
        }
    };
    service.destroySubject = function (instance) {
        return Subject.delete({id: instance.id });
    };
    
    // Visit Type services
    service.visitTypesUpdated = function () {
        $rootScope.$broadcast('visit_types:updated');
    };
    service.getVisitTypes = function(project_id) {
        return VisitType.query(
            {
                'project': project_id
            }
        );
    };
    service.createUpdateVisitType = function(instance) {
        if (instance.id) {
            return VisitType.update(
                {id: instance.id },
                instance
            );
        } else {
            return VisitType.save(instance);
        }
    };
    service.destroyVisitType = function (instance) {
        return VisitType.delete({id: instance.id });
    };
    
    // CellSubsetLabel services
    service.cellSubsetLabelsUpdated = function () {
        $rootScope.$broadcast('cell_subset_labels:updated');
    };
    service.getCellSubsetLabels = function(project_id) {
        return CellSubsetLabel.query(
            {
                'project': project_id
            }
        );
    };
    service.createUpdateCellSubsetLabel = function(instance) {
        if (instance.id) {
            return CellSubsetLabel.update(
                {id: instance.id },
                instance
            );
        } else {
            return CellSubsetLabel.save(instance);
        }
    };
    service.destroyCellSubsetLabel = function (instance) {
        return CellSubsetLabel.delete({id: instance.id });
    };
    
    // Stimulation services
    service.stimulationsUpdated = function () {
        $rootScope.$broadcast('stimulations:updated');
    };
    service.getStimulations = function(project_id) {
        return Stimulation.query(
            {
                'project': project_id
            }
        );
    };
    service.createUpdateStimulation = function(instance) {
        if (instance.id) {
            return Stimulation.update(
                {id: instance.id },
                instance
            );
        } else {
            return Stimulation.save(instance);
        }
    };
    service.destroyStimulation = function (instance) {
        return Stimulation.delete({id: instance.id });
    };
    
    // Panel Template services
    service.panelTemplatesUpdated = function () {
        $rootScope.$broadcast('panel_templates:updated');
    };
    service.getPanelTemplates = function(query_object) {
        return PanelTemplate.query(query_object);
    };
    service.getPanelTemplate = function (panel_template_id) {
        return PanelTemplate.get(
            {
                'id': panel_template_id
            }
        );
    };
    service.createUpdatePanelTemplate = function(instance) {
        if (instance.id) {
            return PanelTemplate.update(
                {id: instance.id },
                instance
            );
        } else {
            return PanelTemplate.save(instance);
        }
    };
    service.destroyPanelTemplate = function (instance) {
        return PanelTemplate.delete({id: instance.id });
    };
    service.setCurrentPanelTemplate = function (value) {
        this.current_panel_template = value;
        $rootScope.$broadcast('current_panel_template:updated');
    };
    service.getCurrentPanelTemplate = function () {
        return this.current_panel_template;
    };
    
    // PanelVariant services
    service.createUpdatePanelVariant = function(instance) {
        if (instance.id) {
            return PanelVariant.update(
                {id: instance.id },
                instance
            );
        } else {
            return PanelVariant.save(instance);
        }
    };
    service.destroyPanelVariant = function (instance) {
        return PanelVariant.delete({id: instance.id });
    };
    
    // Site services
    service.sitesUpdated = function () {
        $rootScope.$broadcast('sites:updated');
    };
    service.getSites = function(project_id) {
        return Site.query(
            {
                'project': project_id
            }
        );
    };
    service.createUpdateSite = function(instance) {
        if (instance.id) {
            return Site.update(
                {id: instance.id },
                instance
            );
        } else {
            return Site.save(instance);
        }
    };
    service.destroySite = function (instance) {
        return Site.delete({id: instance.id });
    };
    service.getProjectSitesWithViewPermission = function(project_id) {
        return new Project({'id': project_id}).getSitesWithPermission(
            'view_site_data'
        );
    };
    service.getProjectSitesWithAddPermission = function(project_id) {
        return new Project({'id': project_id}).getSitesWithPermission(
            'add_site_data'
        );
    };
    service.getProjectSitesWithModifyPermission = function(project_id) {
        return new Project({'id': project_id}).getSitesWithPermission(
            'modify_site_data'
        );
    };
    service.getSitePermissions = function (site_id) {
        return new Site({'id': site_id}).getUserPermissions();
    };

    // Cytometer services
    service.cytometersUpdated = function () {
        $rootScope.$broadcast('cytometers:updated');
    };
    service.getCytometers = function(query_object) {
        return Cytometer.query(query_object);
    };
    service.createUpdateCytometer = function(instance) {
        if (instance.id) {
            return Cytometer.update(
                {id: instance.id },
                instance
            );
        } else {
            return Cytometer.save(instance);
        }
    };
    service.destroyCytometer = function (instance) {
        return Cytometer.delete({id: instance.id });
    };

    // Sample related services
    service.samplesUpdated = function () {
        $rootScope.$broadcast('samples:updated');
    };
    service.getSamples = function(query_object) {
        return Sample.query(query_object);
    };
    service.createUpdateSample = function(instance) {
        if (instance.id) {
            return Sample.update(
                {id: instance.id },
                instance
            );
        } else {
            return Sample.save(instance);
        }
    };
    service.getSampleCSV = function (sample_id) {
        return $http.get(
            '/api/repository/samples/' + sample_id.toString() + '/csv/'
        );
    };
    service.destroySample = function (instance) {
        return Sample.delete({id: instance.id });
    };

    // TODO: see where these are used and remove them
    service.setCurrentSample = function (value) {
        this.current_sample = value;
        $rootScope.$broadcast('sampleChanged');
    };
    service.getCurrentSample = function () {
        return this.current_sample;
    };
    
    // Bead Sample related services
    service.beadSamplesUpdated = function () {
        $rootScope.$broadcast('bead_samples:updated');
    };
    service.getBeadSamples = function(query_object) {
        return BeadSample.query(query_object);
    };
    service.createUpdateBeadSample = function(instance) {
        if (instance.id) {
            return BeadSample.update(
                {id: instance.id },
                instance
            );
        } else {
            return BeadSample.save(instance);
        }
    };
    service.getBeadSampleCSV = function (bead_sample_id) {
        return $http.get(
            '/api/repository/beads/' + bead_sample_id.toString() + '/csv/'
        );
    };
    service.destroyBeadSample = function (instance) {
        return BeadSample.delete({id: instance.id });
    };


    // SampleMetadata related services
    service.getSampleMetadata = function (sample_id) {
        return SampleMetadata.query(
            {
                'sample': sample_id
            }
        );
    };

    // Compensation related services
    service.compensationsUpdated = function () {
        $rootScope.$broadcast('compensations:updated');
    };
    service.getCompensations = function (query_object) {
        return Compensation.query(query_object);
    };
    service.getCompensationCSV = function (comp_id) {
        return Compensation.get_CSV(
            {
                'id': comp_id
            }
        );
    };
    service.createCompensation = function(instance) {
        return Compensation.save(instance);
    };
    service.destroyCompensation = function (instance) {
        return Compensation.delete({id: instance.id });
    };

    // Site Panel services
    service.sitePanelsUpdated = function () {
        $rootScope.$broadcast('site_panels:updated');
    };
    service.getSitePanels = function(query_object) {
        return SitePanel.query(query_object);
    };
    service.getSitePanel = function (site_panel_id) {
        return SitePanel.get(
            {
                'id': site_panel_id
            }
        );
    };
    service.createSitePanel = function(instance) {
        return SitePanel.save(instance);
    };
    service.destroySitePanel = function (instance) {
        return SitePanel.delete({id: instance.id });
    };
    
    // ProcessRequest services
    service.processRequestsUpdated = function () {
        $rootScope.$broadcast('process_requests:updated');
    };
    service.getProcessRequests = function(query_object) {
        return ProcessRequest.query(query_object);
    };
    service.getProcessRequest = function(process_request_id) {
        return ProcessRequest.get(
            { id: process_request_id }
        );
    };
    service.createProcessRequest = function(instance) {
        return ProcessRequest.save(instance);
    };
    service.destroyProcessRequest = function (instance) {
        return ProcessRequest.delete({id: instance.id });
    };
    service.createProcessRequestStage2 = function(instance) {
        return ProcessRequestStage2.save(instance);
    };

    // Subprocess Implementation services
    service.getSubprocessImplementations = function(query_object) {
        return SubprocessImplementation.query(query_object);
    };

    // Subprocess Input services
    service.getSubprocessInputs = function(query_object) {
        return SubprocessInput.query(query_object);
    };

    // SampleCollection services
    service.getSampleCollection = function(sample_collection_id) {
        return SampleCollection.get(
            {
                'id': sample_collection_id
            }
        );
    };
    service.createSampleCollection = function(instance) {
        return SampleCollection.save(instance);
    };

    // SampleCollectionMember services
    service.getSampleCollectionMembers = function(sample_collection_id) {
        return SampleCollectionMember.get(
            {
                'id': sample_collection_id
            }
        );
    };
    service.createSampleCollectionMembers = function(instances) {
        return SampleCollectionMember.save(instances);
    };

    // Process Request Input services
    service.createProcessRequestInputs = function(instances) {
        return ProcessRequestInput.save(instances);
    };

    // SampleCluster services
    service.getSampleClusters = function(pr_id, sample_id) {
        return SampleCluster.query(
            {
                'process_request': pr_id,
                'sample': sample_id
            }
        ).$promise;
    };
    service.getSampleClusterCSV = function (id) {
        return $http.get(
            '/api/repository/sample_clusters/' + id.toString() + '/csv/'
        );
    };

    // ClusterLabel services
    service.clusterLabelsUpdated = function () {
        $rootScope.$broadcast('cluster_labels:updated');
    };
    service.getClusterLabels = function(query_object) {
        return ClusterLabel.query(query_object);
    };
    service.getClusterLabel = function(cluster_label_id) {
        return ClusterLabel.get(
            { id: cluster_label_id }
        );
    };
    service.createClusterLabel = function(instance) {
        return ClusterLabel.save(instance);
    };
    service.destroyClusterLabel = function (instance) {
        return ClusterLabel.delete({id: instance.id });
    };

    return service;
});