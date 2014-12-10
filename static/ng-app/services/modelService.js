/**
 * Created by swhite on 6/11/14.
 */

var service = angular.module('ReFlowApp');

service.factory('ModelService', function(
        $rootScope,
        $http,
        User,
        Marker,
        Fluorochrome,
        Specimen,
        Pretreatment,
        Storage,
        Project,
        SubjectGroup,
        Subject,
        VisitType,
        Stimulation,
        PanelTemplate,
        Site,
        Cytometer,
        SitePanel,
        Sample,
        SampleMetadata,
        Compensation,
        ParameterFunction,
        ParameterValueType,
        ProcessRequest,
        SampleCollection,
        SampleCollectionMember,
        SampleCluster) {
    var service = {};

    service.current_site = null;
    service.current_sample = null;
    service.current_panel_template = null;

    service.user = User.get();

    service.getParameterFunctions = function() {
        return ParameterFunction.query(
            {}
        );
    };

    service.getParameterValueTypes = function() {
        return ParameterValueType.query(
            {}
        );
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
    
    // Marker services
    service.markersUpdated = function () {
        $rootScope.$broadcast('markers:updated');
    };
    service.getMarkers = function() {
        return Marker.query({});
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
    service.getFluorochromes = function() {
        return Fluorochrome.query({});
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

    // Pretreatment services
    service.getPretreatments = function() {
        return Pretreatment.query({});
    };

    // Storage services
    service.getStorages = function() {
        return Storage.query({});
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

    // TODO: see where these are used and remove them
    service.setCurrentSite = function (value) {
        this.current_site = value;
        $rootScope.$broadcast('siteChanged');
    };
    service.getCurrentSite = function () {
        return this.current_site;
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

    // TODO: see where these are used and remove them
    service.setCurrentSample = function (value) {
        this.current_sample = value;
        $rootScope.$broadcast('sampleChanged');
    };
    service.getCurrentSample = function () {
        return this.current_sample;
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
        var response = Compensation.save(instance);
        return response;
    };

    service.destroyCompensation = function (instance) {
        return Compensation.delete({id: instance.id });
    };

    // Site Panel services
    service.getSitePanel = function (site_panel_id) {
        return SitePanel.get(
            {
                'id': site_panel_id
            }
        );
    };
    
    // ProcessRequest services
    service.getProcessRequests = function() {
        return ProcessRequest.query(
            {}
        );
    };

    service.getProcessRequest = function(process_request_id) {
        return ProcessRequest.get(
            { id: process_request_id }
        );
    };

    // SampleCollectionMember services
    service.getSampleCollection = function(sample_collection_id) {
        return SampleCollection.get(
            {
                'id': sample_collection_id
            }
        );
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

    return service;
});