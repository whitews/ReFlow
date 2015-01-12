/**
 * Created by swhite on 2/25/14.
 */

var URLS = {
    'USER':                '/api/repository/users/',
    'CURRENT_USER':        '/api/repository/user/',
    'USER_PERMISSIONS':    '/api/repository/permissions/',
    'PROJECTS':            '/api/repository/projects/',
    'PROJECT_USERS':       '/api/repository/projects/:id/users/',
    'MARKERS':             '/api/repository/markers/',
    'FLUOROCHROMES':       '/api/repository/fluorochromes/',
    'SPECIMENS':           '/api/repository/specimens/',
    'SUBJECT_GROUPS':      '/api/repository/subject_groups/',
    'SITES':               '/api/repository/sites/',
    'SUBJECTS':            '/api/repository/subjects/',
    'PANEL_TEMPLATES':     '/api/repository/panel_templates/',
    'SITE_PANELS':         '/api/repository/site_panels/',
    'CYTOMETERS':          '/api/repository/cytometers/',
    'COMPENSATIONS':       '/api/repository/compensations/',
    'STIMULATIONS':        '/api/repository/stimulations/',
    'SAMPLES':             '/api/repository/samples/',
    'CREATE_SAMPLES':      '/api/repository/samples/add/',
    'SAMPLE_METADATA':     '/api/repository/samplemetadata/',
    'SAMPLE_COLLECTIONS':  '/api/repository/sample_collections/',
    'SAMPLE_COLLECTION_MEMBERS':  '/api/repository/sample_collection_members/',
    'BEAD_SAMPLES':        '/api/repository/beads/',
    'VISIT_TYPES':         '/api/repository/visit_types/',
    'PARAMETER_FUNCTIONS': '/api/repository/parameter_functions/',
    'PARAMETER_VALUE_TYPES': '/api/repository/parameter_value_types/',

    // Process related API URLs
    'WORKERS':                 '/api/repository/workers/',
    'SUBPROCESS_CATEGORIES':      '/api/repository/subprocess_categories/',
    'SUBPROCESS_IMPLEMENTATIONS': '/api/repository/subprocess_implementations/',
    'SUBPROCESS_INPUTS':          '/api/repository/subprocess_inputs/',
    'VERIFY_WORKER':           '/api/repository/verify_worker/',
    'PROCESS_REQUESTS':        '/api/repository/process_requests/',
    'PROCESS_REQUEST_INPUTS':     '/api/repository/process_request_inputs',
    'PROCESS_REQUEST_OUTPUTS':     '/api/repository/process_request_outputs',
    'VIABLE_PROCESS_REQUESTS': '/api/repository/viable_process_requests/',
    'CREATE_PROCESS_REQUEST_OUTPUT':  '/api/repository/process_request_outputs/add/',
    'SAMPLE_CLUSTERS':  '/api/repository/sample_clusters/'
};

var service = angular.module('ReFlowApp');

service
    .factory('User', ['$resource', function ($resource) {
        var User = $resource(
            URLS.USER + ':id',
            {},
            {
                update: { method: 'PUT' }
            }
        );

        return User;
    }])
    .factory('CurrentUser', ['$resource', function ($resource) {
        var CurrentUser = $resource(
            URLS.CURRENT_USER + ':username',
            {
                username: '@username'
            },
            {
                is_user: {method: 'GET'}
            }
        );

        return CurrentUser;
    }])
    .factory('UserPermissions', ['$resource', function ($resource) {
        return $resource(URLS.USER_PERMISSIONS + ':id');
    }])
    .factory('Project', ['$resource', function ($resource) {
        var Project = $resource(
            URLS.PROJECTS + ':id',
            {},
            {
                update: { method: 'PUT' }
            }
        );

        Project.prototype.getSitesWithPermission = function(permission) {
            var sites = $resource(
                URLS.PROJECTS + this.id + '/sites_by_permission/?permission=' + permission,
                {},
                {
                    get: {isArray: true}
                }
            );
            return sites.get();
        };

        Project.prototype.getUserPermissions = function() {
            var perms = $resource(
                URLS.PROJECTS + this.id + '/permissions/',
                {},
                {
                    get: {
                        isArray: false
                    }
                }
            );
            return perms.get();
        };

        return Project;
    }])
    .factory('ProjectUsers', ['$resource', function ($resource) {
        var ProjectUsers = $resource(
            URLS.PROJECT_USERS,
            {},
            {
                get: { isArray: false },
                update: { method: 'PUT' }
            }
        );

        return ProjectUsers;
    }])
    .factory('Site', ['$resource', function ($resource) {
        var Site = $resource(
            URLS.SITES + ':id',
            {},
            {
                update: { method: 'PUT' }
            }
        );

        Site.prototype.getUserPermissions = function() {
            var perms = $resource(
                URLS.SITES + this.id + '/permissions/',
                {},
                {
                    get: {
                        isArray: false
                    }
                }
            );
            return perms.get();
        };

        return Site;
    }])
    .factory('Marker', ['$resource', function ($resource) {
        var Marker = $resource(
            URLS.MARKERS + ':id',
            {},
            {
                update: { method: 'PUT' }
            }
        );

        return Marker;
    }])
    .factory('Fluorochrome', ['$resource', function ($resource) {
        var Fluorochrome = $resource(
            URLS.FLUOROCHROMES + ':id',
            {},
            {
                update: { method: 'PUT' }
            }
        );

        return Fluorochrome;
    }])
    .factory('Specimen', ['$resource', function ($resource) {
        var Specimen = $resource(
            URLS.SPECIMENS + ':id',
            {},
            {
                update: { method: 'PUT' }
            }
        );

        return Specimen;
    }])
    .factory('Worker', ['$resource', function ($resource) {
        var Worker = $resource(
            URLS.WORKERS + ':id',
            {},
            {
                update: { method: 'PUT' }
            }
        );

        return Worker;
    }])
    .factory('SubjectGroup', ['$resource', function ($resource) {
        var SubjectGroup = $resource(
            URLS.SUBJECT_GROUPS + ':id',
            {},
            {
                update: { method: 'PUT' }
            }
        );

        return SubjectGroup;
    }])
    .factory('Subject', ['$resource', function ($resource) {
        var Subject = $resource(
            URLS.SUBJECTS + ':id',
            {},
            {
                update: { method: 'PUT' }
            }
        );

        return Subject;
    }])
    .factory('VisitType', ['$resource', function ($resource) {
        var VisitType = $resource(
            URLS.VISIT_TYPES + ':id',
            {},
            {
                update: { method: 'PUT' }
            }
        );

        return VisitType;
    }])
    .factory('Stimulation', ['$resource', function ($resource) {
        var Stimulation = $resource(
            URLS.STIMULATIONS + ':id',
            {},
            {
                update: { method: 'PUT' }
            }
        );

        return Stimulation;
    }])
    .factory('Cytometer', ['$resource', function ($resource) {
        var Cytometer = $resource(
            URLS.CYTOMETERS + ':id',
            {},
            {
                update: { method: 'PUT' }
            }
        );

        return Cytometer;
    }])
    .factory('PanelTemplate', ['$resource', function ($resource) {
        return $resource(
            URLS.PANEL_TEMPLATES + ':id',
            {},
            {
                update: {
                    method: 'PUT'
                }
            }
        );
    }])
    .factory('SitePanel', ['$resource', function ($resource) {
        var SitePanel = $resource(
            URLS.SITE_PANELS + ':id',
            {},
            {
                get: { isArray: false },
                query: { url: URLS.SITE_PANELS, isArray: true }
            }
        );

        return SitePanel;
    }])
    .factory('Compensation', ['$resource', function ($resource) {
        var Compensation =  $resource(
            URLS.COMPENSATIONS + ':id',
            {},
            {
                get_CSV: {
                    url: URLS.COMPENSATIONS + ':id/object/',
                    isArray: false
                }
            }
        );

        return Compensation;
    }])
    .factory('Sample', ['$resource', function ($resource) {
        var Sample = $resource(
            URLS.SAMPLES + ':id',
            {},
            {
                update: { method: 'PUT' }
            }
        );

        return Sample;
    }])
    .factory('SampleMetadata', ['$resource', function ($resource) {
        return $resource(URLS.SAMPLE_METADATA, {});
    }])
    .factory('SampleCollection', ['$resource', function ($resource) {
        var SampleCollection = $resource(
            URLS.SAMPLE_COLLECTIONS + ':id',
            {},
            {
                get: { isArray: false }
            }
        );

        return SampleCollection;
    }])
    .factory('SampleCollectionMember', ['$resource', function ($resource) {
        return $resource(
            URLS.SAMPLE_COLLECTION_MEMBERS,
            {},
            {
                save: {
                    method: 'POST',
                    isArray: true
                }
            }
        );
    }])
    .factory('BeadSample', ['$resource', function ($resource) {
        var BeadSample = $resource(
            URLS.BEAD_SAMPLES + ':id',
            {},
            {
                update: { method: 'PUT' }
            }
        );

        return BeadSample;
    }])
    .factory('SubprocessCategory', ['$resource', function ($resource) {
        return $resource(URLS.SUBPROCESS_CATEGORIES);
    }])
    .factory('SubprocessImplementation', ['$resource', function ($resource) {
        return $resource(URLS.SUBPROCESS_IMPLEMENTATIONS);
    }])
    .factory('SubprocessInput', ['$resource', function ($resource) {
        return $resource(URLS.SUBPROCESS_INPUTS);
    }])
    .factory('ProcessRequest', ['$resource', function ($resource) {
        var ProcessRequest = $resource(
            URLS.PROCESS_REQUESTS + ':id',
            {},
            {
                get: { isArray: false }
            }
        );

        return ProcessRequest;
    }])
    .factory('ProcessRequestInput', ['$resource', function ($resource) {
        return $resource(
            URLS.PROCESS_REQUEST_INPUTS,
            {},
            {
                save: {
                    method: 'POST',
                    isArray: true
                }
            }
        );
    }])
    .factory('ProcessRequestOutput', ['$resource', function ($resource) {
        return $resource(URLS.PROCESS_REQUEST_OUTPUTS);
    }])
    .factory('SampleCluster', ['$resource', function ($resource) {
        return $resource(URLS.SAMPLE_CLUSTERS);
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