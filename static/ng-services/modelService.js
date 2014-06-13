/**
 * Created by swhite on 6/11/14.
 */

var service = angular.module('modelService', []);

service.factory('ModelService', function($rootScope, $location) {
    var model = {};
    model.current_project = null;

    model.setCurrentProject = function (value) {
        this.current_project = value;
        $rootScope.$broadcast('projectChanged');
    };

    model.getCurrentProject = function () {
        return this.current_project;
    };

    return model;
});