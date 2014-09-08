/**
 * Created by swhite on 6/11/14.
 */

var service = angular.module('ReFlowApp');

service.factory('ModelService', function($rootScope, User, Marker, Fluorochrome, Project, Site, ParameterFunction, ParameterValueType) {
    var model = {};
    model.current_site = null;
    model.current_sample = null;
    model.current_panel_template = null;

    model.user = User.get();

    function refresh_projects() {
        model.projects = Project.query();

        model.projects.$promise.then(function (projects) {
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

    //model.markers = Marker.query();
    model.getMarkers = function() {
        return Marker.query();
    };

    model.fluorochromes = Fluorochrome.query();

    model.getFluorochromes = function () {
        return this.fluorochromes;
    };

    model.getParameterFunctions = function() {
        return ParameterFunction.query(
            {}
        );
    };

    model.getParameterValueTypes = function() {
        return ParameterValueType.query(
            {}
        );
    };

    model.getProjects = function () {
        return $rootScope.projects;
    };
    model.reloadProjects = function () {
        refresh_projects();
    };

    model.getProjectById = function(id) {
        var project = $.grep($rootScope.projects, function(e){ return e.id == id; });
        if (project.length > 0) {
            return project[0];
        }
        return null;
    };

    model.setCurrentSite = function (value) {
        this.current_site = value;
        $rootScope.$broadcast('siteChanged');
    };

    model.getCurrentSite = function () {
        return this.current_site;
    };

    model.setCurrentSample = function (value) {
        this.current_sample = value;
        $rootScope.$broadcast('sampleChanged');
    };

    model.getCurrentSample = function () {
        return this.current_sample;
    };

    model.setCurrentPanelTemplate = function (value) {
        this.current_panel_template = value;
        $rootScope.$broadcast('panelTemplateChanged');
    };

    model.getCurrentPanelTemplate = function () {
        return this.current_panel_template;
    };

    return model;
});