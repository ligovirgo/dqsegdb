<?php
/*
DQSEGDB - Convert segdb-format data to DQSEGDB.
*/

// Set constants.
class Constants {
	
	public $host;
	public $db;
	public $db_segdb;
	public $db_user;
	public $db_pass;

	public $source_dir;
	
	public $package_version;
	
	public $use_join_in_segment_conversion;
	public $use_process_coalescence;
	
	// DB & server connection constants.
	public function db_connection_constants() {
		$this->host = "localhost";
		$this->db = "dqsegdb_s6_tmp";
		$this->db_user = "admin";
		$this->db_pass = "lvdb_11v35";
	}

	// Source file constants.
	public function source_constants() {
//		$this->source_dir = "/root/imports/geosegdb/Feb112015/";
		$this->source_dir = "/root/imports/s6segdb/";
	}

	// Package version constants.
	public function package_version_constants() {
		$this->package_version = "2.0";
	}

	// Package execution constants.
	public function package_execution_constants() {
		$this->use_join_in_segment_conversion = FALSE;	// TRUE = GEO-type data dictionary (fewer segments); FALSE = S6-type data dictionary.
		$this->use_process_coalescence = FALSE;			// TRUE = GEO-type data dictionary (lots of process + args); FALSE = S6-type data dictionary.
	}
}

?>