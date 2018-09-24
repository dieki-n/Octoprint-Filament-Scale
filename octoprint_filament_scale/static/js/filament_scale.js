/*
 * View model for OctoPrint-Filament_scale
 *
 * Author: Victor Noordhoek
 * License: AGPLv3
 */
 
 
 
$(function() {
    function Filament_scaleViewModel(parameters) {
        var self = this;
		self.printerState = parameters[0]
		self.settings = parameters[1]
		self.last_raw_weight = 0
		self.calibrate_known_weight = 0
        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];

        // TODO: Implement your plugin's view model here.
		self.printerState.filamentRemainingString = ko.observable("Loading...")
		self.tare = function(){
			
			self.settings.settings.plugins.filament_scale.tare(self.last_raw_weight)
			weight = self.getWeight(self.last_raw_weight)
			self.settings.settings.plugins.filament_scale.lastknownweight(weight)
			
			self.printerState.filamentRemainingString(self.getOutputWeight(weight))
		};
		self.calibrate = function(){
			
			weight = Math.round((self.last_raw_weight - self.settings.settings.plugins.filament_scale.tare()))
			if (weight != 0 && self.calibrate_known_weight != 0){
				self.settings.settings.plugins.filament_scale.reference_unit(weight / self.calibrate_known_weight)
				weight = self.getWeight(self.last_raw_weight)
				self.settings.settings.plugins.filament_scale.lastknownweight(weight)
				self.printerState.filamentRemainingString(self.getOutputWeight(weight))
			} else {
				error_message = {"tare": self.settings.settings.plugins.filament_scale.tare(),
								"r_u": self.settings.settings.plugins.filament_scale.reference_unit(),
								"parsed_r_u": parseInt(self.settings.settings.plugins.filament_scale.reference_unit()),
								"known_weight": self.calibrate_known_weight,
								"spool_weight": self.settings.settings.plugins.filament_scale.spool_weight(),
								"weight": weight,
								"raw_weight":self.last_raw_weight}
				console.log(error_message)
			}
			
		}
		self.onDataUpdaterPluginMessage = function(plugin, message){
			
				
			self.last_raw_weight = parseInt(message)
			if (parseInt(message) == 8388608){
				self.printerState.filamentRemainingString("Sensor Not Connected")
				self.settings.settings.plugins.filament_scale.lastknownweight("Error")
			} else {
				weight = self.getWeight(message)
				if (Number.isNaN(weight)){
					error_message = {"tare": self.settings.settings.plugins.filament_scale.tare(),
									"r_u": self.settings.settings.plugins.filament_scale.reference_unit(),
									"parsed_r_u": parseInt(self.settings.settings.plugins.filament_scale.reference_unit()),
									"message" : message,
									"known_weight": self.calibrate_known_weight,
									"spool_weight": self.settings.settings.plugins.filament_scale.spool_weight()}
					console.log(error_message)
					self.settings.settings.plugins.filament_scale.lastknownweight("Error")
					self.printerState.filamentRemainingString("Calibration Error")				 
				} else{
					self.settings.settings.plugins.filament_scale.lastknownweight(weight)
					self.printerState.filamentRemainingString(self.getOutputWeight(weight))
				}
			}
		};
		self.getWeight = function(weight){
			return Math.round((parseInt(weight) - self.settings.settings.plugins.filament_scale.tare()) / parseInt(self.settings.settings.plugins.filament_scale.reference_unit()))
		}
		self.getOutputWeight = function(weight){
			return (Math.max(weight - self.settings.settings.plugins.filament_scale.spool_weight(), 0) + "g")
		}
		self.onStartup = function() {
            var element = $("#state").find(".accordion-inner [data-bind='text: stateString']");
            if (element.length) {
                var text = gettext("Filament Remaining");
                element.after("<br>" + text + ": <strong data-bind='text: filamentRemainingString'></strong>");
            }
        };
		
	}
	
    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: Filament_scaleViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: ["printerStateViewModel", "settingsViewModel"],
        // Elements to bind to, e.g. #settings_plugin_filament_scale, #tab_plugin_filament_scale, ...
        elements: ["#settings_plugin_filament_scale"]
    });
});
