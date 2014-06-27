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
