/**
 * Created by swhite on 6/11/14.
 */

var service = angular.module('ReFlowApp');

service.factory('ModelService', function(
        $rootScope,
        User,
        Marker,
        Fluorochrome,
        Project,
        Site,
        ParameterFunction,
        ParameterValueType,
        ProcessRequest) {
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

    service.setCurrentSample = function (value) {
        this.current_sample = value;
        $rootScope.$broadcast('sampleChanged');
    };

    service.getCurrentSample = function () {
        return this.current_sample;
    };

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

    service.createUpdateProcessRequest = function(instance) {
        var errors = null;
        var response;

        if (instance.id) {
            response = ProcessRequest.update(
                {id: instance.id },
                instance
            );
        } else {
            response = ProcessRequest.save(instance);
        }

        response.$promise.then(function () {
            // let everyone know the process_requestss have changed
            $rootScope.$broadcast('process_requestss:updated');
        }, function (error) {
            errors = error.data;
        });

        return errors;
    };

    return service;
});