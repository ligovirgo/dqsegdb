//# Copyright (C) 2014-2020 Syracuse University, European Gravitational Observatory, and Christopher Newport University.  Written by Ryan Fisher and Gary Hemming. See the NOTICE file distributed with this work for additional information regarding copyright ownership.

//# This program is free software: you can redistribute it and/or modify

//# it under the terms of the GNU Affero General Public License as

//# published by the Free Software Foundation, either version 3 of the

//# License, or (at your option) any later version.

//#

//# This program is distributed in the hope that it will be useful,

//# but WITHOUT ANY WARRANTY; without even the implied warranty of

//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the

//# GNU Affero General Public License for more details.

//#

//# You should have received a copy of the GNU Affero General Public License

//# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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