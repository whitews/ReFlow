app.controller(
    'ModalFormCtrl',
    [
        '$scope',
        '$modalInstance',
        'instance',
        function ($scope, $modalInstance, instance) {
            $scope.instance = instance;
            $scope.ok = function () {
                $modalInstance.close();
            };
        }
    ]
);