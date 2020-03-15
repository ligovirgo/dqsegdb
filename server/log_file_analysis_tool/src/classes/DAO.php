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

/*****************************
 * DQSEGDB Log-file analyser *
* *************************/

/* Get libraries. */
require_once 'Constants.php';
require_once 'Logger.php';

/* Data Access Object class. */
class DAO {
	
	public $pdo;

	/////////////////////////
	// GENERAL CONNECTION //
	///////////////////////

	/* Connect to database. */
	public function db_connect() {
		// Instantiate.
		$constant = new Constants();
		$log = new Logger();
		// Get database-connection constants.
		$constant->db_connection_constants();
		// If connection not made.
		if(!$this->pdo) {
			// Create new PDO object.
			$this->pdo = new PDO("mysql:host=".$constant->db_host.";dbname=".$constant->db, $constant->db_user, $constant->db_pass);
			// If PDO object not set.
			if(!isset($this->pdo)) {
				// Write to log.
				$log->write_to_log_file(4, "Unable to connect to database.");
				// Write verbose.
				$log->write_verbose_to_error_stack(NULL, $stmt->errorInfo());
				exit();
			}
			// Otherwise, no connection values are available.
			else {
				// Write to log.
				$log->write_to_log_file(4, "No database connection variables are available.");
			}
		}
	}
	
	////////////////////////
	// INSERT OPERATIONS //
	//////////////////////

	/* Insert a URI call response time. */
	public function insert_response_time($method, $uri, $call_time, $reply_time, $response_time) {
		// Init.
		$r = FALSE;
		$args = NULL;
		// Instantiate.
		$log = new Logger();
		// Create PDO object
		$this->db_connect();
		// Split the URI between trunk and args.
		$a_uri = explode('?', $uri);
		// Get the URI call ID.
		$uri_id_array = $this->get_uri_id_array($method, $a_uri[0]);
		// If args are available.
		if(isset($a_uri[1])) {
			// Set the args.
			$args = $a_uri[1];
		}
		// If the URI ID array contains data.
		if(!empty($uri_id_array)) {
			// Build prepared statement.
			if($stmt = $this->pdo->prepare("INSERT INTO tbl_uri_calls
											(http_method_fk,
											 uri_fk,
											 uri_args,
											 call_date_time,
											 call_date_time_ms,
											 reply_date_time,
											 reply_date_time_ms,
											 response_time_ms)
											VALUES
											(:m, :u, :ua, :c, :cm, :r, :rm, :rt)")) {
				// If statement not executed.
				if($stmt->execute(array(':m' => $uri_id_array['http_method_id'],
										':u' => $uri_id_array['uri_id'],
										':ua' => $args,
										':c' => substr($call_time, 0, 19),
										':cm' => substr($call_time, 21, 3),
										':r' => substr($reply_time, 0, 19),
										':rm' => substr($reply_time, 21, 3),
										':rt' => $response_time))) {
					// Set return value.
					$r = TRUE;
				}
				else {
					// Write to log.
					$log->write_to_log_file(3, "Problem inserting response times URI: ".$method." - ".$uri." (".$call_time."). Statement not executed.");
					// Write verbose.
					$log->write_verbose_to_error_stack(NULL, $stmt->errorInfo());
				}
			}
		}
		else {
			// Write to log.
			$log->write_to_log_file(3, "There was a problem somewhere in the response-time insertion cycle.");
		}
		// Return.
		return $r;
	}
	
	/* Insert a URI. */
	public function insert_uri($m, $u) {
		// Init.
		$r = FALSE;
		// Instantiate.
		$log = new Logger();
		// Create PDO object
		$this->db_connect();
		// Get the method ID array.
		$a_methods = $this->get_reverse_http_method_array();
		// Build prepared statement.
		if($stmt = $this->pdo->prepare("INSERT INTO tbl_uri
										(http_method_fk, uri)
										VALUES
										(:m, :u)")) {
			// If statement not executed.
			if($stmt->execute(array(':m' => $a_methods[$m],
									':u' => $u))) {
				// Set return value.
				$r = TRUE;
			}
			else {
				// Write to log.
				$log->write_to_log_file(3, "Problem inserting URI: ".$m." - ".$u.". Statement not executed.");
				// Write verbose.
				$log->write_verbose_to_error_stack(NULL, $stmt->errorInfo());
			}
		}
		// Return.
		return $r;
	}

	////////////////////////
	// SELECT OPERATIONS //
	//////////////////////
	
	/* Get HTTP-method array. */
	public function get_http_method_array() {
		// Init.
		$a = array();
		// Instantiate.
		$log = new Logger();
		// Create PDO object
		$this->db_connect();
		// Build prepared statement.
		if($stmt = $this->pdo->prepare("SELECT *
										FROM tbl_http_methods")) {
			// If statement executes.
			if($stmt->execute()) {
				// Bind by column name.
				$stmt->bindColumn('http_method_id', $http_method_id);
				$stmt->bindColumn('http_method', $http_method);
				// Loop.
				while($stmt->fetch()) {
					// Set.
					$a[$http_method_id] = $http_method;
				}
			}
			// Otherwise.
			else {
				// Write to log.
				$log->write_to_log_file(3, "Problem retrieving HTTP method array. Statement not executed.");
				// Write verbose.
				$log->write_verbose_to_error_stack(NULL, $stmt->errorInfo());
			}
		}
		// Return.
		return $a;
	}
	
	/* Get reverse HTTP-method array. */
	public function get_reverse_http_method_array() {
		// Init.
		$a = array();
		// Instantiate.
		$log = new Logger();
		// Create PDO object
		$this->db_connect();
		// Build prepared statement.
		if($stmt = $this->pdo->prepare("SELECT *
										FROM tbl_http_methods")) {
			// If statement executes.
			if($stmt->execute()) {
				// Bind by column name.
				$stmt->bindColumn('http_method_id', $http_method_id);
				$stmt->bindColumn('http_method', $http_method);
				// Loop.
				while($stmt->fetch()) {
					// Set.
					$a[$http_method] = $http_method_id;
				}
			}
			// Otherwise.
			else {
				// Write to log.
				$log->write_to_log_file(3, "Problem retrieving reverse HTTP method array. Statement not executed.");
				// Write verbose.
				$log->write_verbose_to_error_stack(NULL, $stmt->errorInfo());
			}
		}
		// Return.
		return $a;
	}
	
	/* Get IDs related to a specific HTTP method and URI. */
	public function get_uri_id_array($m, $u) {
		// Init.
		$a = array();
		// Instantiate.
		$log = new Logger();
		// Create PDO object
		$this->db_connect();
		// Build prepared statement.
		if($stmt = $this->pdo->prepare("SELECT http_method_id, uri_id
										FROM tbl_uri
										LEFT JOIN tbl_http_methods ON tbl_uri.http_method_fk = tbl_http_methods.http_method_id
										WHERE http_method=:m AND uri=:u
										LIMIT 1")) {
			// If statement executes.
			if($stmt->execute(array(':m' => $m, ':u' => $u))) {
				// Bind by column name.
				$stmt->bindColumn('http_method_id', $http_method_id);
				$stmt->bindColumn('uri_id', $uri_id);
				// Loop.
				while($stmt->fetch()) {
					// Set.
					$a = array('http_method_id' => $http_method_id,
							   'uri_id' => $uri_id);
				}
				// If no ID has been found.
				if(empty($a)) {
					// If the URI is inserted successfully.
					if($this->insert_uri($m, $u)) {
						// Re-call this function.
						$a = $this->get_uri_id_array($m, $u);
					}
				}
			}
			// Otherwise.
			else {
				// Write to log.
				$log->write_to_log_file(3, "Problem retrieving reverse HTTP method array. Statement not executed.");
				// Write verbose.
				$log->write_verbose_to_error_stack(NULL, $stmt->errorInfo());
			}
		}
		// Return.
		return $a;
	}
		
}

?>