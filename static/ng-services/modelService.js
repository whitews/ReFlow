/**
 * Created by swhite on 6/11/14.
 */

var service = angular.module('modelService', []);

service.factory('ModelService', function($rootScope, $location) {
    var model = {};
    model.current_project = null;
    model.current_sample = null;
    model.current_panel_template = null;

    model.setCurrentProject = function (value) {
        this.current_project = value;
        $rootScope.$broadcast('projectChanged');
    };

    model.getCurrentProject = function () {
        return this.current_project;
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