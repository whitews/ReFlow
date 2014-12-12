app.controller(
    'UserController',
    [
        '$scope',
        '$controller',
        'ModelService',
        function ($scope, $controller, ModelService) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            function get_list() {
                // first, get the list of users
                var response = ModelService.getProjectUsers(
                    $scope.current_project.id
                );
                var users = [];
                response.$promise.then(function (data) {
                    if (!data.hasOwnProperty('users')) {
                        return;
                    }
                    data.users.forEach(function (username) {
                        // create a user object and add to users
                        var user = {'username': username};
                        users.push(user);

                        // get user's project-level permissions for current
                        // project
                        user.project_permissions = ModelService.getUserPermissions(
                            'project',
                            $scope.current_project.id,
                            user.username
                        );

                        // get user's site-level  permissions for sites in the
                        // current project
                        user.sites = [];
                        $scope.sites.forEach(function (site) {
                            var site_perm_response = ModelService.getUserPermissions(
                                'site',
                                site.id,
                                user.username
                            );
                            site_perm_response.$promise.then(function (perms) {
                                if (perms.length > 0) {
                                    var site_copy = angular.copy(site);
                                    site_copy.permissions = perms;
                                    user.sites.push(site_copy);
                                }
                            })
                        });
                    });
                });
                return users;
            }
            if ($scope.current_project) {
                $scope.sites = ModelService.getSites($scope.current_project.id);
                $scope.sites.$promise.then(function () {
                    $scope.users = get_list();
                })
            }
            $scope.$on('current_project:updated', function () {
                $scope.sites = ModelService.getSites($scope.current_project.id);
                $scope.sites.$promise.then(function () {
                    $scope.users = get_list();
                })
            });
            $scope.$on('user_permissions:updated', function () {
                $scope.sites = ModelService.getSites($scope.current_project.id);
                $scope.sites.$promise.then(function () {
                    $scope.users = get_list();
                })
            });
        }
    ]
);

app.controller(
    'UserQueryController',
    [
        '$scope',
        '$controller',
        'ModelService',
        function ($scope, $controller, ModelService) {
            $controller('ModalController', {$scope: $scope});

            $scope.user_test = null;

            $scope.query_user = function(username) {
                // TODO: check if user already has some permissions for
                // this project and/or its sites
                var user_test = ModelService.isUser(username);

                user_test.$promise.then(function (o) {
                    $scope.chosen_user = {
                        username: username,
                        project_permissions: [],
                        sites: []
                    };
                    $scope.user_test = true;
                }, function () {  // error
                    $scope.user_test = false;
                });
            };
        }
    ]
);


app.controller(
    'UserEditController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.current_project = ModelService.current_project;

            // Build user management form values
            $scope.project_permissions = {
                'view_project_data': {'name': 'View Project Data', 'value': false },
                'add_project_data': {'name': 'Add Project Data', 'value': false },
                'modify_project_data': {'name': 'Modify Project Data', 'value': false },
                'submit_process_requests': {'name': 'Submit Process Requests', 'value': false},
                'manage_project_users': {'name': 'Manage Project Users', 'value': false }
            };

            $scope.instance.project_permissions.forEach(function (user_perm) {
                if ($scope.project_permissions.hasOwnProperty(user_perm.permission_codename)) {
                    $scope.project_permissions[user_perm.permission_codename].id = user_perm.id;
                    $scope.project_permissions[user_perm.permission_codename].value = true;
                }
            });

            var site_perms = {
                'view_site_data': {'name': 'View Site Data', 'value': false },
                'add_site_data': {'name': 'Add Site Data', 'value': false },
                'modify_site_data': {'name': 'Modify Site Data', 'value': false }
            };

            $scope.site_permissions = {};

            // build default site perms
            $scope.sites = ModelService.getSites($scope.current_project.id);

            $scope.sites.$promise.then(function () {
                init_site_perms();
            });

            function init_site_perms() {
                var site_perm_obj;
                $scope.sites.forEach(function (site) {
                    site_perm_obj = {
                        'id': null,
                        'obj_id': site.id,
                        'site_name': site.site_name,
                        'permissions': angular.copy(site_perms)
                    };

                    $scope.site_permissions[site.id] = site_perm_obj;
                });

                // now populate with any site perms the current user instance has
                $scope.instance.sites.forEach(function (site) {
                    if ($scope.site_permissions.hasOwnProperty(site.id)) {
                        site.permissions.forEach(function (site_perm) {
                            if ($scope.site_permissions[site.id].permissions.hasOwnProperty(site_perm.permission_codename)) {
                                $scope.site_permissions[site.id].permissions[site_perm.permission_codename].id = site_perm.id;
                                $scope.site_permissions[site.id].permissions[site_perm.permission_codename].value = true;
                            }
                        });
                    }
                });
            }

            $scope.checkbox_changed = function (codename, perm, model, obj_id) {
                perm.errors = [];
                var response;
                if (perm.value) {
                    response = ModelService.destroyUserPermission(perm);
                } else {
                    response = ModelService.createUserPermission(
                        model,
                        obj_id,
                        $scope.instance.username,
                        codename
                    );
                }

                response.$promise.then(function (o) {
                    perm.id = o.id;
                    // notify to update user permissions list
                    ModelService.userPermissionsUpdated();
                }, function (error) {
                    perm.errors = error.data;
                });
            };
        }
    ]
);
