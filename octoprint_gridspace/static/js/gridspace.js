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
            if (current === "#tab_plugin_gridspace" && !self.gridspace_initialized()) {
                $('#gridspace_iframe').attr("src", "https://grid.space/kiri/");
                self.gridspace_initialized(true);
            }
        };
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: gridSpaceViewModel,
        dependencies: ["settingsViewModel"],
        elements: [ /* ... */ ]
    });
});
