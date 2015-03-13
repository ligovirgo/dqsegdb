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
	
	// DB & server connection constants.
	public function db_connection_constants() {
		$this->host = "localhost";
		$this->db = "dqsegdb";
		$this->db_user = "{MYSQL_USER}";
		$this->db_pass = "{MYSQL_PASSWORD}";
	}

	// Source file constants.
	public function source_constants() {
		$this->source_dir = "/path/to/csv/source/files/";
	}

	// Package version constants.
	public function package_version_constants() {
		$this->package_version = "v1r1";
	}
}

?>