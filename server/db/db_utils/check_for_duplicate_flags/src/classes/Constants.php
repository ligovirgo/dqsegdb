<?php
/*
DQSEGDB - Check for duplicate flags in the database, taking into account the underscore as wildcard character.
*/

// Set constants.
class Constants {
	
	public $host;
	public $db;
	public $db_segdb;
	public $db_user;
	public $db_pass;

	public $package_version;
	
	public $flags_to_receive_merged_data;
	
	// DB & server connection constants.
	public function db_connection_constants() {
		$this->host = "localhost";
		$this->db = "dqsegdb";
		$this->db_user = "admin";
		$this->db_pass = "lvdb_11v35";
	}

	// Package version constants.
	public function package_version_constants() {
		$this->package_version = "1.0";
	}
	
	// Flag constants.
	public function flag_constants() {
		$this->flags_to_receive_merged_data = array();
	}

}

?>