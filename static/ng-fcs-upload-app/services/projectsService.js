/**
 * Created by swhite on 2/25/14.
 */

app.service('projectsService', function ($http) {

    this.getProjects = function () {
        return $http.get
    }

});