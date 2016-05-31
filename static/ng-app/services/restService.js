/**
 * Created by swhite on 2/25/14.
 */

var URLS = {
    'USER':                '/api/repository/users/',
    'CURRENT_USER':        '/api/repository/user/',
    'CHANGE_PASSWORD':     '/api/repository/user/change_password/',
    'RESET_PASSWORD':     '/api/repository/user/reset_password/',
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
    'PANEL_VARIANT':       '/api/repository/panel_variants/',
    'SITE_PANELS':         '/api/repository/site_panels/',
    'COMPENSATIONS':       '/api/repository/compensations/',
    'CELL_SUBSET_LABELS':  '/api/repository/cell_subset_labels/',
    'STIMULATIONS':        '/api/repository/stimulations/',
    'SAMPLES':             '/api/repository/samples/',
    'CREATE_SAMPLES':      '/api/repository/samples/add/',
    'SAMPLE_METADATA':     '/api/repository/samplemetadata/',
    'SAMPLE_COLLECTIONS':  '/api/repository/sample_collections/',
    'SAMPLE_COLLECTION_MEMBERS':  '/api/repository/sample_collection_members/',
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
    'PROCESS_REQUEST_STAGE_2': '/api/repository/process_requests/stage2/',
    'PROCESS_REQUEST_INPUTS':     '/api/repository/process_request_inputs',
    'VIABLE_PROCESS_REQUESTS': '/api/repository/viable_process_requests/',
    'SAMPLE_CLUSTERS':  '/api/repository/sample_clusters/',
    'CLUSTER_LABELS':  '/api/repository/cluster_labels/'
};

var service = angular.module('ReFlowApp');

service
    .factory('User', ['$resource', function ($resource) {
        var User = $resource(
            URLS.USER + ':id',
            {},
            {
                update: { method: 'PUT' },
                change_password: {
                    method: 'PUT',
                    url: URLS.CHANGE_PASSWORD
                },
                reset_password: {
                    method: 'PUT',
                    url: URLS.RESET_PASSWORD
                }
            }
        );

        return User;
    }])
    .factory('CurrentUser', ['$resource', function ($resource) {
        var CurrentUser = $resource(
            URLS.CURRENT_USER,
            {},
            {
                is_user: {
                    method: 'POST',
                    url: URLS.CURRENT_USER + 'exists/'
                }
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
    .factory('CellSubsetLabel', ['$resource', function ($resource) {
        var CellSubsetLabel = $resource(
            URLS.CELL_SUBSET_LABELS + ':id',
            {},
            {
                update: { method: 'PUT' }
            }
        );

        return CellSubsetLabel;
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
    .factory('PanelVariant', ['$resource', function ($resource) {
        var PanelVariant = $resource(
            URLS.PANEL_VARIANT + ':id',
            {},
            {
                update: { method: 'PUT' }
            }
        );

        return PanelVariant;
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
                get: { isArray: false },
                get_progress: {
                    url: URLS.PROCESS_REQUESTS + ':id/progress/',
                    isArray: false
                }
            }
        );

        return ProcessRequest;
    }])
    .factory('ProcessRequestStage2', ['$resource', function ($resource) {
        return $resource(URLS.PROCESS_REQUEST_STAGE_2, {});
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
    .factory('SampleCluster', ['$resource', function ($resource) {
        return $resource(URLS.SAMPLE_CLUSTERS);
    }])
    .factory('ClusterLabel', ['$resource', function ($resource) {
        var ClusterLabel = $resource(
            URLS.CLUSTER_LABELS + ':id',
            {},
            {}
        );
        return ClusterLabel;
    }])
    .factory('ParameterFunction', ['$resource', function ($resource) {
        return $resource(URLS.PARAMETER_FUNCTIONS);
    }])
    .factory('ParameterValueType', ['$resource', function ($resource) {
        return $resource(URLS.PARAMETER_VALUE_TYPES);
    }])
    .service('Pretreatment', [ function () {
        this.query = function () {
            return [
                {
                    name:'In vitro'
                },
                {
                    name:'Ex vivo'
                },
                {
                    name:'Comp Beads'
                },
                {
                    name:'Untreated'
                }
            ];
        };
    }])
    .service('StainingType', [ function () {
        this.query = function () {
            return [
                {
                    abbreviation: 'FULL',
                    name: 'Full Stain'
                },
                {
                    abbreviation: 'FMO',
                    name: 'Fluorescence Minus One'
                },
                {
                    abbreviation: 'ISO',
                    name: 'Isotype Control'
                },
                {
                    abbreviation: 'UNS',
                    name: 'Unstained'
                },
                {
                    abbreviation: 'COMP',
                    name: 'Compensation Beads'
                }
            ];
        };
    }])
    .service('Storage', [ function () {
        this.query = function () {
            return [
                {
                    name:'Fresh'
                },
                {
                    name:'Cryopreserved'
                },
                {
                    name:'Comp Beads'
                }
            ];
        };
    }]);