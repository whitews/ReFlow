/**
 * Created by swhite on 2/25/14.
 */

var URLS = {
    'PROJECTS':            '/api/repository/projects/',
    'MARKERS':             '/api/repository/markers/',
    'FLUOROCHROMES':       '/api/repository/fluorochromes/',
    'SPECIMENS':           '/api/repository/specimens/',
    'SUBJECT_GROUPS':      '/api/repository/subject_groups/',
    'SITES':               '/api/repository/sites/',
    'SUBJECTS':            '/api/repository/subjects/',
    'PROJECT_PANELS':      '/api/repository/project_panels/',
    'SITE_PANELS':         '/api/repository/site_panels/',
    'CYTOMETERS':          '/api/repository/cytometers/',
    'COMPENSATIONS':       '/api/repository/compensations/',
    'CREATE_COMPENSATION': '/api/repository/compensations/add/',
    'STIMULATIONS':        '/api/repository/stimulations/',
    'SAMPLES':             '/api/repository/samples/',
    'CREATE_SAMPLES':      '/api/repository/samples/add/',
    'SAMPLE_METADATA':     '/api/repository/samplemetadata/',
    'VISIT_TYPES':         '/api/repository/visit_types/',
    'PARAMETER_FUNCTIONS': '/api/repository/parameter_functions/',
    'PARAMETER_VALUE_TYPES': '/api/repository/parameter_value_types/',

    // Process related API URLs
    'WORKERS':                 '/api/repository/workers/',
    'VERIFY_WORKER':           '/api/repository/verify_worker/',
    'PROCESS_REQUESTS':        '/api/repository/process_requests/',
    'VIABLE_PROCESS_REQUESTS': '/api/repository/viable_process_requests/',
    'CREATE_PROCESS_REQUEST_OUTPUT':  '/api/repository/process_request_outputs/add/'
};

var service = angular.module('reflowService', ['ngResource']);

service
    .factory('Project', ['$resource', function ($resource) {
        return $resource(URLS.PROJECTS);
    }])
    .factory('Site', ['$resource', function ($resource) {
        return $resource(URLS.SITES);
    }])
    .factory('Marker', ['$resource', function ($resource) {
        return $resource(URLS.MARKERS);
    }])
    .factory('Fluorochrome', ['$resource', function ($resource) {
        return $resource(URLS.FLUOROCHROMES);
    }])
    .factory('Specimen', ['$resource', function ($resource) {
        return $resource(URLS.SPECIMENS);
    }])
    .factory('SubjectGroup', ['$resource', function ($resource) {
        return $resource(URLS.SUBJECT_GROUPS);
    }])
    .factory('Subject', ['$resource', function ($resource) {
        return $resource(URLS.SUBJECTS);
    }])
    .factory('VisitType', ['$resource', function ($resource) {
        return $resource(URLS.VISIT_TYPES);
    }])
    .factory('Stimulation', ['$resource', function ($resource) {
        return $resource(URLS.STIMULATIONS);
    }])
    .factory('Cytometer', ['$resource', function ($resource) {
        return $resource(URLS.CYTOMETERS);
    }])
    .factory('ProjectPanel', ['$resource', function ($resource) {
        return $resource(URLS.PROJECT_PANELS);
    }])
    .factory('SitePanel', ['$resource', function ($resource) {
        return $resource(URLS.SITE_PANELS);
    }])
    .factory('Compensation', ['$resource', function ($resource) {
        return $resource(URLS.COMPENSATIONS);
    }])
    .factory('Sample', ['$resource', function ($resource) {
        return $resource(URLS.SAMPLES);
    }])
    .factory('ParameterFunction', ['$resource', function ($resource) {
        return $resource(URLS.PARAMETER_FUNCTIONS);
    }])
    .factory('ParameterValueType', ['$resource', function ($resource) {
        return $resource(URLS.PARAMETER_VALUE_TYPES);
    }])
    .service('Pretreatment', [ function () {
        this.query = function () {
            return [{name:'In vitro'}, {name:'Ex vivo'}];
        };
    }])
    .service('Storage', [ function () {
        this.query = function () {
            return [{name:'Fresh'}, {name:'Cryopreserved'}];
        };
    }]);