<?php

// Initialise variables.
class Constants {

	public $bg_warning;
	public $bg_error;
	
	// Get background constants.
	public function get_bg_constants() {
		$this->bg_warning = ' style="color: #ffffff; background-color: #FFA500";';
		$this->bg_error = ' style="color: #ffffff; background-color: #FF0000";';
	}

}

?>