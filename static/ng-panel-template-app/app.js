var app = angular.module(
    'PanelTemplateApp',
    [
        'ngRoute',
        'ngSanitize',
        'ngCookies',
        'ui.bootstrap',
        'ui.select2',
        'reflowService'
    ]
);

app.config(function ($routeProvider) {
    $routeProvider
        .when('/',
        {
            controller: 'MainController',
            templateUrl: '/static/ng-panel-template-app/partials/create_panel_template.html'
        })
        .when('/edit/:template_id',
        {
            controller: 'MainController',
            templateUrl: '/static/ng-panel-template-app/partials/create_panel_template.html'
        });
});
app.run(function ($http, $cookies) {
    $http.defaults.headers.common['X-CSRFToken'] = $cookies['csrftoken'];
});