<?php

/*******************************
* DQSEGDB - Log-file analyser *
*****************************/

/* Constants-handling class */
class Constants {

	public $db_host;
	public $db;
	public $db_user;
	public $db_pass;
	
	public $host;
	public $app_doc_root;
	
	public $minimum_response_time;
	
	public $bg_warning;
	public $bg_error;
	
	public $output_format;
	public $analyse_dir;
	public $output_dir;
		
	public $log_dir;
	public $log_levels;
	public $log_current_level;
	public $log_verbose;
	
	/* DB & server connection constants. */
	public function db_connection_constants() {
		$this->db_host = "localhost";
		$this->db = "dqsegdb_log_file_analysis";
		$this->db_user = "root";
		$this->db_pass = "";
	}
	
	/* Get general constants. */
	public function get_general_constants() {
		$this->host = 'dqsegdb6';
		$this->app_doc_root = 'dqsegdb_lfa';
	}
	
	/* Get time constants. */
	public function get_time_constants() {
		$this->minimum_response_time = 0;
	}
	
	/* Get background constants. */
	public function get_bg_constants() {
		$this->bg_warning = ' style="color: #ffffff; background-color: #FFA500";';
		$this->bg_error = ' style="color: #ffffff; background-color: #FF0000";';
	}
	
	/* Get file constants. */
	public function get_file_constants() {
		// Get host.
		$this->get_general_constants();
		// Output format.
		$this->output_format = 'sql';	// Options: csv; sql.
		// Log file directory to be read.
		$this->analyse_dir = 'data/analyse';
		// Produced CSV output file.
		$this->output_dir = 'output/'.$this->host.'_processed_'.date('Ymd').".".$this->output_format;
	}

	/* Get logger constants. */
	public function logger_constants() {
		// Get host.
		$this->get_general_constants();
		// Set.
		$this->log_dir = $_SERVER['PWD'].'/'.'logs';
		$this->log_levels = array('INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL');
		$this->log_current_level = 0;
		$this->log_verbose = TRUE;
	}

}

?>