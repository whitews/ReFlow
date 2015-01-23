app.controller(
    'UserChangePasswordController',
    [
        '$scope',
        'ModelService',
        function ($scope, ModelService) {
            $scope.change_password = function (instance) {
                $scope.errors = [];
                var response = ModelService.changeUserPassword(
                    instance.id,
                    instance.current_password,
                    instance.password
                );

                response.$promise.then(function () {
                    // notify to update list
                    ModelService.usersUpdated();

                    // close modal
                    $scope.ok();

                }, function (error) {
                    $scope.errors = error.data;
                });
            };
        }
    ]
);