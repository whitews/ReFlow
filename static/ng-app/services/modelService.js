/**
 * Created by swhite on 6/11/14.
 */

var service = angular.module('ReFlowApp');

service.factory('ModelService', function(
        $rootScope,
        $http,
        $q,
        User,
        Marker,
        Fluorochrome,
        Project,
        SubjectGroup,
        Subject,
        VisitType,
        Stimulation,
        PanelTemplate,
        Site,
        Cytometer,
        SitePanel,
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

    service.getMarkers = function() {
        return Marker.query();
    };

    service.getFluorochromes = function () {
        return Fluorochrome.query();
    };

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

    service.createUpdateProject = function(instance) {
        var errors = null;
        var response;

        if (instance.id) {
            response = Project.update(
                {id: instance.id },
                instance
            );
        } else {
            response = Project.save(instance);
        }

        $q.all([response.$promise]).then(function () {
            // let everyone know the projects have changed
            $rootScope.$broadcast('projects:updated');
        }, function (error) {
            errors = error.data;
        });

        return errors;
    };

    // Subject Group services
    service.getSubjectGroups = function(project_id) {
        return SubjectGroup.query(
            {
                'project': project_id
            }
        );
    };

    service.createUpdateSubjectGroup = function(instance) {
        var errors = null;
        var response;

        if (instance.id) {
            response = SubjectGroup.update(
                {id: instance.id },
                instance
            );
        } else {
            response = SubjectGroup.save(instance);
        }

        $q.all([response.$promise]).then(function () {
            // let everyone know the subject groups have changed
            $rootScope.$broadcast('subject_groups:updated');
        }, function (error) {
            errors = error.data;
        });

        return errors;
    };

    service.destroySubjectGroup = function (instance) {
        var errors = null;
        var response;

        response = SubjectGroup.delete({id: instance.id });

        $q.all([response.$promise]).then(function () {
            // let everyone know the subject groups have changed
            $rootScope.$broadcast('subject_groups:updated');
        }, function (error) {
            errors = error.data;
        });

        return errors;
    };
    
    // Subject services
    service.getSubjects = function(project_id) {
        return Subject.query(
            {
                'project': project_id
            }
        );
    };

    service.createUpdateSubject = function(instance) {
        var errors = null;
        var response;

        if (instance.id) {
            response = Subject.update(
                {id: instance.id },
                instance
            );
        } else {
            response = Subject.save(instance);
        }

        $q.all([response.$promise]).then(function () {
            // let everyone know the subject groups have changed
            $rootScope.$broadcast('subjects:updated');
        }, function (error) {
            errors = error.data;
        });

        return errors;
    };

    service.destroySubject = function (instance) {
        var errors = null;
        var response;

        response = Subject.delete({id: instance.id });

        $q.all([response.$promise]).then(function () {
            // let everyone know the subjects have changed
            $rootScope.$broadcast('subjects:updated');
        }, function (error) {
            errors = error.data;
        });

        return errors;
    };
    
    // Visit Type services
    service.getVisitTypes = function(project_id) {
        return VisitType.query(
            {
                'project': project_id
            }
        );
    };

    service.createUpdateVisitType = function(instance) {
        var errors = null;
        var response;

        if (instance.id) {
            response = VisitType.update(
                {id: instance.id },
                instance
            );
        } else {
            response = VisitType.save(instance);
        }

        $q.all([response.$promise]).then(function () {
            // let everyone know the visit types have changed
            $rootScope.$broadcast('visit_types:updated');
        }, function (error) {
            errors = error.data;
        });

        return errors;
    };

    service.destroyVisitType = function (instance) {
        var errors = null;
        var response;

        response = VisitType.delete({id: instance.id });

        $q.all([response.$promise]).then(function () {
            // let everyone know the visit types have changed
            $rootScope.$broadcast('visit_types:updated');
        }, function (error) {
            errors = error.data;
        });

        return errors;
    };
    
    // Stimulation services
    service.getStimulations = function(project_id) {
        return Stimulation.query(
            {
                'project': project_id
            }
        );
    };

    service.createUpdateStimulation = function(instance) {
        var errors = null;
        var response;

        if (instance.id) {
            response = Stimulation.update(
                {id: instance.id },
                instance
            );
        } else {
            response = Stimulation.save(instance);
        }

        $q.all([response.$promise]).then(function () {
            // let everyone know the stimulations have changed
            $rootScope.$broadcast('stimulations:updated');
        }, function (error) {
            errors = error.data;
        });

        return errors;
    };

    service.destroyStimulation = function (instance) {
        var errors = null;
        var response;

        response = Stimulation.delete({id: instance.id });

        $q.all([response.$promise]).then(function () {
            // let everyone know the stimulations have changed
            $rootScope.$broadcast('stimulations:updated');
        }, function (error) {
            errors = error.data;
        });

        return errors;
    };
    
    // Panel Template services
    service.destroyPanelTemplate = function (instance) {
        var errors = null;
        var response;

        response = PanelTemplate.delete({id: instance.id });

        $q.all([response.$promise]).then(function () {
            // let everyone know the panel templates have changed
            $rootScope.$broadcast('panel_templates:updated');
        }, function (error) {
            errors = error.data;
        });

        return errors;
    };
    
    // Site services
    service.getSites = function(project_id) {
        return Site.query(
            {
                'project': project_id
            }
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

    service.createUpdateSite = function(instance) {
        var errors = null;
        var response;

        if (instance.id) {
            response = Site.update(
                {id: instance.id },
                instance
            );
        } else {
            response = Site.save(instance);
        }

        $q.all([response.$promise]).then(function () {
            // let everyone know the sites have changed
            $rootScope.$broadcast('sites:updated');
        }, function (error) {
            errors = error.data;
        });

        return errors;
    };

    service.destroySite = function (instance) {
        var errors = null;
        var response;

        response = Site.delete({id: instance.id });

        $q.all([response.$promise]).then(function () {
            // let everyone know the sites have changed
            $rootScope.$broadcast('sites:updated');
        }, function (error) {
            errors = error.data;
        });

        return errors;
    };

    // Cytometer services
    service.getCytometers = function(query_object) {
        return Cytometer.query(query_object);
    };
    
    service.createUpdateCytometer = function(instance) {
        var errors = null;
        var response;

        if (instance.id) {
            response = Cytometer.update(
                {id: instance.id },
                instance
            );
        } else {
            response = Cytometer.save(instance);
        }

        $q.all([response.$promise]).then(function () {
            // let everyone know the cytometers have changed
            $rootScope.$broadcast('cytometers:updated');
        }, function (error) {
            errors = error.data;
        });

        return errors;
    };
    
    service.destroyCytometer = function (instance) {
        var errors = null;
        var response;

        response = Cytometer.delete({id: instance.id });

        $q.all([response.$promise]).then(function () {
            // let everyone know the cytometers have changed
            $rootScope.$broadcast('cytometers:updated');
        }, function (error) {
            errors = error.data;
        });

        return errors;
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
    service.setCurrentSample = function (value) {
        this.current_sample = value;
        $rootScope.$broadcast('sampleChanged');
    };

    service.getCurrentSample = function () {
        return this.current_sample;
    };

    service.getSampleCSV = function (sample_id) {
        return $http.get(
            '/api/repository/samples/' + sample_id.toString() + '/csv/'
        );
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

    // Panel related services
    service.setCurrentPanelTemplate = function (value) {
        this.current_panel_template = value;
        $rootScope.$broadcast('panelTemplateChanged');
    };

    service.getCurrentPanelTemplate = function () {
        return this.current_panel_template;
    };
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