/**
 * Created by swhite on 6/11/14.
 */

var service = angular.module('ReFlowApp');

service.factory('ModelService', function($rootScope, Marker, Fluorochrome) {
    var model = {};
    model.current_project = null;
    model.current_site = null;
    model.current_sample = null;
    model.current_panel_template = null;

    model.markers = Marker.query();
    model.fluorochromes = Fluorochrome.query();

    model.getMarkers = function () {
        return this.markers;
    };

    model.getFluorochromes = function () {
        return this.fluorochromes;
    };

    model.setProjects = function (object) {
        this.projects = object;
        $rootScope.$broadcast('projectsChanged');
    };

    model.getProjects = function () {
        return this.projects;
    };

    model.getProjectById = function(id) {
        var project = $.grep(this.projects, function(e){ return e.id == id; });
        if (project.length > 0) {
            return project[0];
        }
        return null;
    };

    model.setCurrentProject = function (object) {
        this.current_project = object;
        $rootScope.$broadcast('projectChanged');
    };

    model.getCurrentProject = function () {
        return this.current_project;
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