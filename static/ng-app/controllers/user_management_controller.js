app.controller(
    'UserController',
    [
        '$scope',
        '$controller',
        '$modal',
        'ProjectUser',
        'UserPermissions',
        function ($scope, $controller, $modal, ProjectUser, UserPermissions) {
            // Inherits ProjectDetailController $scope
            $controller('ProjectDetailController', {$scope: $scope});

            function get_list() {
                // first, get the list of users
                var response = ProjectUser.get(
                    { 'id': $scope.current_project.id }
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
                        user.project_permissions = UserPermissions.query(
                            {
                                'model': 'project',
                                'object_pk': $scope.current_project.id,
                                'username': user.username
                            }
                        );

                        // get user's site-level  permissions for sites in the
                        // current project
                        user.sites = [];
                        $scope.current_project.sites.forEach(function (site) {
                            site_perm_response = UserPermissions.query(
                                {
                                    'model': 'site',
                                    'object_pk': site.id,
                                    'username': user.username
                                }
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
            $scope.users = get_list();

            $scope.$on('updateUsers', function () {
                $scope.users = get_list();
            });

            $scope.init_form = function(instance) {
                var proposed_instance = angular.copy(instance);
                $scope.errors = [];

                // launch form modal
                var modalInstance = $modal.open({
                    templateUrl: 'static/ng-app/partials/user-form.html',
                    controller: ModalFormCtrl,
                    resolve: {
                        instance: function() {
                            return proposed_instance;
                        }
                    }
                });
            };
        }
    ]
);

app.controller(
    'UserEditController',
    ['$scope', '$rootScope', '$controller', 'UserPermissions', function ($scope, $rootScope, $controller, UserPermissions) {
        // Inherits ProjectDetailController $scope
        $controller('UserController', {$scope: $scope});

        // Build user management form values
        $scope.project_permissions = {
            'view_project_data': {'name': 'View Project Data', 'value': false },
            'add_project_data': {'name': 'Add Project Data', 'value': false },
            'modify_project_data': {'name': 'Modify Project Data', 'value': false },
            'manage_project_users': {'name': 'Manage Project Users', 'value': false }
        };

        $scope.instance.project_permissions.forEach(function (user_perm) {
            if ($scope.project_permissions.hasOwnProperty(user_perm.permission_codename)) {
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
        $scope.current_project.sites.forEach(function (site) {
            var site_perm_obj = {
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
                        $scope.site_permissions[site.id].permissions[site_perm.permission_codename].value = true;
                    }
                });
            }
        });

        $scope.create_update = function (instance) {
            $scope.errors = [];
            var response;
            if (instance.id) {
                response = UserPermissions.update(
                    {id: instance.id },
                    $scope.instance
                );
            } else {
                instance.project = $scope.current_project.id;

                response = UserPermissions.save(
                    $scope.instance
                );
            }

            response.$promise.then(function () {
                // notify to update subject group list
                $rootScope.$broadcast('updateUserPermissions');

                // close modal
                $scope.ok();

            }, function (error) {
                $scope.errors = error.data;
            });
        };
    }
]);
