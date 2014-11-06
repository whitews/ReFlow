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
        Project,
        Site,
        SampleMetadata,
        Compensation,
        ParameterFunction,
        ParameterValueType,
        ProcessRequest,
        SampleCollectionMember,
        SampleCluster) {
    var service = {};
    service.current_site = null;
    service.current_sample = null;
    service.current_panel_template = null;

    service.user = User.get();

    function refresh_projects() {
        service.projects = Project.query();

        service.projects.$promise.then(function (projects) {
            $rootScope.projects = projects;
            projects.forEach(function (p) {
                p.getUserPermissions().$promise.then(function (value) {
                    p.permissions = value.permissions;
                });

                p.update_sites = function() {
                    // Add user's sites
                    p.sites = [];
                    var sites = Site.query({project: p.id});
                    sites.$promise.then(function (sites) {
                        sites.forEach(function (s) {
                            s.can_modify = false;
                            p.sites.push(s);
                            s.getUserPermissions().$promise.then(function (value) {
                                s.permissions = value.permissions;
                                if (value.hasOwnProperty('permissions')) {
                                    value.permissions.forEach(function (p) {
                                        if (p === 'modify_site_data') {
                                            s.can_modify = true;
                                        }
                                    });
                                }
                            });
                        });

                        // create site lookup by primary key
                        p.site_lookup = {};
                        for (var i = 0, len = p.sites.length; i < len; i++) {
                            p.site_lookup[p.sites[i].id] = p.sites[i];
                        }
                    });
                };

                p.update_sites();

            });
            $rootScope.$broadcast('projectsUpdated');
        });
    }

    service.getMarkers = function() {
        return Marker.query();
    };

    service.fluorochromes = Fluorochrome.query();

    service.getFluorochromes = function () {
        return this.fluorochromes;
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

    service.getProjects = function () {
        return $rootScope.projects;
    };
    service.reloadProjects = function () {
        refresh_projects();
    };

    service.getProjectById = function(id) {
        var project = $.grep($rootScope.projects, function(e){ return e.id == id; });
        if (project.length > 0) {
            return project[0];
        }
        return null;
    };

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
    service.getCompensations = function (site_panel_id, acq_date) {
        return Compensation.query(
            {
                'site_panel': site_panel_id,
                'acquisition_date': acq_date
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
    service.getSampleCollectionMembers = function(sample_collection_id) {
        return SampleCollectionMember.query(
            {
                'sample_collection': sample_collection_id
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
        );
    };

    return service;
});