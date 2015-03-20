<?php

// Set error reporting.
ini_set("display_errors","1");

// Initialise variables.
class Variables {

	public $host;
	public $db;
	public $db_user;
	public $db_pass;

	public $server_host;
	
	public $doc_root;
	public $download_dir;
	
	public $ad_type;
	public $c;

	public function initVariables() {
		// DB & server connection variables.
		$this->host = "localhost";
		$this->db = "dqsegdb_wui";
		$this->db_user = "admin";
		$this->db_pass = "lvdb_11v35";
	}
	
	// Set file-related variables.
	public function get_file_related_variables() {
		$this->doc_root = '/usr/share/dqsegdb_wui/';
		$this->download_dir = 'downloads/';
	}
	
	// Get admin type.
	public function getAdminType() {
		if(isset($_GET["ad_type"])) {
			$this->ad_type = $_GET["ad_type"];
		}
	}

	// Get content call ID.
	public function getContentCallID() {
		if(isset($_GET["c"])) {
			$this->c = $_GET["c"];
		}
		else {
			$this->c = 1;
		}
	}

	// Initialise sessions.
	public function initialise_sessions() {
		if(!isset($_SESSION['default_gps_start'])) {
			$_SESSION['default_gps_start'] = '';
		}
		if(!isset($_SESSION['default_gps_stop'])) {
			$_SESSION['default_gps_stop'] = '';
		}
		if(!isset($_SESSION['changing_current_host'])) {
			$_SESSION['changing_current_host'] = FALSE;
		}
		if(!isset($_SESSION['flag_choice_option'])) {
			$_SESSION['flag_choice_option'] = 0;
		}
	}
}

?>