<?php

// Set error reporting.
ini_set("display_errors","1");
require_once "DAO.php";


// Initialise variables.
class Variables {

	public $app_version;
	public $max_selectable_flags;
	public $payloads_to_display;
	public $payloads_to_display_on_homepage;
	public $rts_to_display;
	public $payloads_page_counter_display_diff;
	public $rts_page_counter_display_diff;
	public $default_filter_start_page;
	public $default_rts_filter_start_page;
	public $default_backup_filter_start_page;
	public $backups_to_display;
	public $backups_to_display_on_homepage;
	public $backups_page_counter_display_diff;
	
	public $host;
	public $host_rts;
	public $db;
	public $db_rts;
	public $db_user;
	public $db_pass;

	public $server_host;
	
	public $doc_root;
	public $download_dir;
	public $python_utilities_dir;
	
	public $req;
	public $c;

	public function get_app_variables() {
		// Application-related variables.
		$this->app_version = "1.9";
		$this->max_selectable_flags = 10;
		$this->default_filter_start_page = 1;
		$this->payloads_to_display = 20;
		$this->payloads_to_display_on_homepage = 5;
		$this->payloads_page_counter_display_diff = 5;
		$this->rts_to_display = 30;
		$this->default_rts_filter_start_page = 1;
		$this->rts_payloads_page_counter_display_diff = 5;
		$this->default_backup_filter_start_page = 1;
		$this->backups_to_display = 30;
		$this->backups_to_display_on_homepage = 5;
		$this->backups_page_counter_display_diff = 5;
	}
	
	public function initVariables() {
		// DB & server connection variables.
		$this->host = "localhost";
		$this->host_rts = "segments-backup.ligo.org";
		$this->db = "dqsegdb_web";
		$this->db_rts = "dqsegdb_regression_tests";
		$this->db_user = "admin";
		$this->db_pass = "lvdb_11v35";
	}
	
	// Set file-related variables.
	public function get_file_related_variables() {
		$this->doc_root = '/usr/share/dqsegdb_web/';
		$this->download_dir = 'downloads/';
		$this->python_utilities_dir = 'python_utilities/';
	}
	
	// Get request.
	public function getReq() {
		if(isset($_GET["req"])) {
			$this->req = $_GET["req"];
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
       	$dao = new DAO();
        // Get default format key from db
        $format_array = $dao->get_specific_value_by_group_and_add_int(4,1);
		// Get app variables.
		$this->get_app_variables();
		// Set sessions.
		if(!isset($_SESSION['default_gps_start'])) {
			$_SESSION['default_gps_start'] = '';
		}
		if(!isset($_SESSION['default_gps_stop'])) {
			$_SESSION['default_gps_stop'] = '';
		}
		if(!isset($_SESSION['default_output_format'])) {
                    $_SESSION['default_output_format'] = key($format_array);
                    #echo "format_array key from InitVar: ";
                    #print_r(key($format_array));
		}
		if(!isset($_SESSION['default_output_history'])) {
		    $_SESSION['default_output_history'] = 0;
                    #echo "history_array key from InitVar: ";
                    #print_r(0);
		}
		if(!isset($_SESSION['changing_current_host'])) {
			$_SESSION['changing_current_host'] = FALSE;
		}
			if(!isset($_SESSION['flag_choice_option'])) {
			$_SESSION['flag_choice_option'] = 0;
		}
		if(!isset($_SESSION['filter_user'])) {
			$_SESSION['filter_user'] = 0;
		}
		if(!isset($_SESSION['filter_data'])) {
			$_SESSION['filter_data'] = 0;
		}
		if(!isset($_SESSION['filter_start_page'])) {
			$_SESSION['filter_start_page'] = $this->default_filter_start_page;
		}
		if(!isset($_SESSION['rts_filter_start_page'])) {
			$_SESSION['rts_filter_start_page'] = $this->default_rts_filter_start_page;
		}
    	if(!isset($_SESSION['backup_filter_start_page'])) {
			$_SESSION['backup_filter_start_page'] = $this->default_backup_filter_start_page;
		}
		if(!isset($_SESSION['uri_deselected'])) {
			$_SESSION['uri_deselected'] = array();
		}
	}
}

?>
