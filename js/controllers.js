var fritureApp = angular.module('fritureApp', []);

fritureApp.controller('ReleasesCtrl', function ($scope, $http) {
  $http.get('https://api.github.com/repos/tlecomte/friture/releases/latest').success(function(data) {
    $scope.latest = data;
    $scope.windowsAsset = data.assets.filter(function(asset) { return asset.name.match(/.msi$/); })[0];
    $scope.macAsset = data.assets.filter(function(asset) { return asset.name.match(/.dmg$/); })[0];
    $scope.linuxAsset = data.assets.filter(function(asset) { return asset.name.match(/.AppImage$/); })[0];
  });
});

fritureApp.filter('bytes', function() {
    return function(bytes, precision) {
        if (isNaN(parseFloat(bytes)) || !isFinite(bytes)) return '-';
        if (typeof precision === 'undefined') precision = 1;
        var units = ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'],
            number = Math.floor(Math.log(bytes) / Math.log(1024));
        return (bytes / Math.pow(1024, Math.floor(number))).toFixed(precision) +  ' ' + units[number];
    }
});