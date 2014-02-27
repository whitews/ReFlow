/**
 * Created by swhite on 2/25/14.
 */

var URLS = {
    'TOKEN':               '/api/token-auth/',
    'PROJECTS':            '/api/repository/projects/',
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

    // Process related API URLs
    'PROCESSES':               '/api/repository/processes/',
    'WORKERS':                 '/api/repository/workers/',
    'VERIFY_WORKER':           '/api/repository/verify_worker/',
    'PROCESS_REQUESTS':        '/api/repository/process_requests/',
    'VIABLE_PROCESS_REQUESTS': '/api/repository/viable_process_requests/',
    'CREATE_PROCESS_REQUEST_OUTPUT':  '/api/repository/process_request_outputs/add/'
};

app.factory('Project', ['$resource', function ($resource) {

    return $resource(URLS.PROJECTS);

}]);

app.factory('Site', ['$resource', function ($resource) {

    return $resource(URLS.SITES + ':project');

}]);