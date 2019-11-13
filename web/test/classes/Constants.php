<?php
/*
This file is part of the DQSEGDB WUI.

This file was written by Gary Hemming <gary.hemming@ego-gw.it>.

DQSEGDB WUI uses the following open source software:
- jQuery JavaScript Library v1.12.4, available under the MIT licence - http://jquery.org/license - Copyright jQuery Foundation and other contributors.
- W3.CSS 2.75 by Jan Egil and Borge Refsnes.
- Font Awesome by Dave Gandy - http://fontawesome.io.
- Jquery Timepicker, developed and maintained by Willington Vega. Code licensed under the MIT and GPL licenses - http://timepicker.co
*/

/* Set constants. */
class Constants {
	
	public $db_host;
	public $db;
	public $db_user;
	public $db_pass;
	
	public $app_name;
	public $app_uri;
	public $yn_array;
	public $yn_inverse_array;
	public $off_on_array;
	public $include_history_default;
	public $choose_flag_option_default;
	public $max_selectable_flags;
	
	public $doc_root;
	public $download_dir;
	public $python_utilities_dir;
	
	public $log_dir;
	public $log_levels;
	public $log_current_level;
	public $log_verbose;
	
	/* DB & server connection constants. */
	public function db_connection_constants() {
	    $this->db_host = "localhost";
	    $this->db = "dqsegdb_web_new";
	    $this->db_user = "root";
	    $this->db_pass = "";
	}
	
	/* General constants. */
	public function general_constants() {
		$this->app_name = 'DQSEGDB';
		$this->app_uri = 'https://segments-web.ligo.org/';
        $this->yn_array = array(0 => 'No', 1 => 'Yes');
        $this->yn_inverse_array = array(0 => 'Yes', 1 => 'No');
        $this->off_on_array = array(0 => 'Off', 1 => 'On');
        $this->include_history_default = 0;
        $this->choose_flag_option_default = 0;
        $this->max_selectable_flags = 10;
	}
	
	// Set file-related variables.
	public function get_file_related_variables() {
	    $this->doc_root = '/usr/share/dqsegdb/web/test/';
	    $this->download_dir = 'downloads/';
	    $this->python_utilities_dir = 'python_utilities/';
	}
	
	/* Logger constants. */
	public function logger_constants() {
		// Set.
		$this->log_dir = '/var/log/dqsegdb_wui';
		$this->log_levels = array('INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL');
		$this->log_current_level = 0;
		$this->log_verbose = TRUE;
	}
	
}

?>
