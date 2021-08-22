/*
 * View model for OctoPrint-Iframe
 *
 * Author: jneilliii
 * License: MIT
 */
$(function() {
    function gridSpaceViewModel(parameters) {
        let self = this;
        self.gridspace_initialized = ko.observable(false);
        self.settingsViewModel = parameters[0];

        self.onTabChange = function(current, previous) {
            if (current === "#tab_plugin_gridspace"){
                self.initialize_gridspace();
            }
        };

        self.onAfterBinding = function(){
            self.settingsViewModel.settings.plugins.gridspace.show_help.subscribe(function(data){
                self.initialize_gridspace();
            });
        };

        self.initialize_gridspace = function(){
            if (self.settingsViewModel.settings.plugins.gridspace.show_help()) {
                $('#gridspace_iframe').attr("src", "https://grid.space/op.html");
                self.gridspace_initialized(false);
            } else if (!self.gridspace_initialized()) {
                $('#gridspace_iframe').attr("src", "https://grid.space/kiri");
                self.gridspace_initialized(true);
            }
        };

        self.maximize_gridspace = function() {
            $('#tab_plugin_gridspace').toggleClass('gs_fullscreen');
        };

        self.hide_help = function() {
            self.settingsViewModel.settings.plugins.gridspace.show_help(false);
            self.settingsViewModel.saveData();
        };
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: gridSpaceViewModel,
        dependencies: ["settingsViewModel"],
        elements: [ "#settings_plugin_gridspace", "#tab_plugin_gridspace" ]
    });
});
