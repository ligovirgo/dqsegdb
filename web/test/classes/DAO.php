<?php
/*
This file is part of the DQSEGDB WUI.

This file was written by Gary Hemming <gary.hemming@ego-gw.it>.

DQSEGDB WUI uses the following open source software:
- jQuery JavaScript Library v1.12.4, available under the MIT licence - http://jquery.org/license - Copyright jQuery Foundation and other contributors.
- W3.CSS 2.79 by Jan Egil and Borge Refsnes.
- Font Awesome by Dave Gandy - http://fontawesome.io.
- Jquery Timepicker, developed and maintained by Willington Vega. Code licensed under the MIT and GPL licenses - http://timepicker.co
*/

// Get libraries.
require_once 'Constants.php';
require_once 'Logger.php';
require_once 'Utils.php';

/* Data Access Object class. */
class DAO {
	
	public $pdo;

	/**********************
	* GENERAL CONNECTION *
	********************/

	/* Connect to database. */
	public function db_connect() {
		// Instantiate.
		$log = new Logger();
		// Create new variables object.
		$constant = new Constants();
		$constant->db_connection_constants();
		// If connection not made.
		if(!$this->pdo) {
			// Create new PDO object.
		    $this->pdo = new PDO("mysql:host=".$constant->db_host.";dbname=".$constant->db, $constant->db_user, $constant->db_pass);
			// If PDO object not set.
			if(!isset($this->pdo)) {
				// Write to log.
				$log->write_to_log_file(4, "Unable to connect to database.");
				exit();
			}
			else {
			    // Ensure UTF-8 used.
			    $this->ensure_utf8();
			}
		}
	}
	
	/* Ensure UTF-8 used. */
	private function ensure_utf8() {
	    // Instantiate.
	    $log = new Logger();
	    // Create PDO object
	    $this->db_connect();
	    // Build prepared statement.
	    if($stmt = $this->pdo->prepare("SET NAMES UTF8")) {
			// If statement executes.
    	    if(!$stmt->execute()) {
    	        // Write to log.
    	        $log->write_to_log_file(3, "Problem setting character set to UTF-8. Statement not executed.");
    	        // Write verbose.
    	        $log->write_verbose_to_error_stack(NULL, $stmt->errorInfo());
    	    }
	    }
	}
	
	/******************
	 * HOST FUNCTIONS *
	 ******************/
	
	/* Get the ID of the default host. */
	public function get_default_host() {
	    // Init.
	    $r = 0;
	    // Instantiate.
	    $log = new Logger();
	    // Create PDO object
	    $this->db_connect();
	    // Build prepared statement.
	    if($stmt = $this->pdo->prepare("SELECT host_id
										FROM tbl_hosts
										WHERE host_default=1
                                        LIMIT 1")) {
			// If statement executes.
    	    if($stmt->execute()) {
    	        // Bind by column name.
    	        $stmt->bindColumn('host_id', $host_id);
    	        // Loop.
    	        while($stmt->fetch()) {
    	            // Set.
    	            $r = $host_id;
    	        }
    	    }
    	    // Otherwise.
    	    else {
    	        // Write to log.
    	        $log->write_to_log_file(3, "Problem retrieving ID of default host. Statement not executed.");
    	        // Write verbose.
    	        $log->write_verbose_to_error_stack(NULL, $stmt->errorInfo());
    	    }
	    }
	    // Return.
	    return $r;
	}

	/* Get an array of details relating to a specific host. */
	public function get_host_details($h) {
	    // Init.
	    $a = array();
	    // Instantiate.
	    $log = new Logger();
	    // Create PDO object
	    $this->db_connect();
	    // Build prepared statement.
	    if($stmt = $this->pdo->prepare("SELECT *
										FROM tbl_hosts
										WHERE host_id=:h
                                        LIMIT 1")) {
            // If statement executes.
    	    if($stmt->execute(array(':h' => $h))) {
    	        // Fetch the result.
    	        $a = $stmt->fetchAll();
    	    }
    	    // Otherwise.
    	    else {
    	        // Write to log.
    	        $log->write_to_log_file(3, "Problem retrieving array of details for host ID: ".$h.". Statement not executed.");
    	        // Write verbose.
    	        $log->write_verbose_to_error_stack(NULL, $stmt->errorInfo());
    	    }
	    }
	    // Return.
	    return $a;
	}
	
	/***************************
	 * OUTPUT-FORMAT FUNCTIONS *
	 **************************/
	
	/* Get an array of available output-formats. */
	public function get_output_formats() {
	    // Init.
	    $a = array();
	    // Instantiate.
	    $log = new Logger();
	    // Create PDO object
	    $this->db_connect();
	    // Build prepared statement.
	    if($stmt = $this->pdo->prepare("SELECT *
										FROM tbl_output_formats")) {
            // If statement executes.
    	    if($stmt->execute()) {
    	        // Fetch the result.
    	        $a = $stmt->fetchAll();
    	    }
    	    // Otherwise.
    	    else {
    	        // Write to log.
    	        $log->write_to_log_file(3, "Problem retrieving array of output formats. Statement not executed.");
    	        // Write verbose.
    	        $log->write_verbose_to_error_stack(NULL, $stmt->errorInfo());
    	    }
	    }
	    // Return.
	    return $a;
	}
	
	/* Get the ID of the default output format. */
	public function get_default_output_format() {
	    // Init.
	    $r = 0;
	    $output_format_id = 0;
	    // Instantiate.
	    $log = new Logger();
	    // Create PDO object
	    $this->db_connect();
	    // Build prepared statement.
	    if($stmt = $this->pdo->prepare("SELECT output_format_id
										FROM tbl_output_formats
										WHERE output_format_default=1
                                        LIMIT 1")) {
            // If statement executes.
    	    if($stmt->execute()) {
    	        // Bind by column name.
    	        $stmt->bindColumn('output_format_id', $output_format_id);
    	        // Loop.
    	        while($stmt->fetch()) {
    	            // Set.
    	            $r = $output_format_id;
    	        }
    	    }
    	    // Otherwise.
    	    else {
    	        // Write to log.
    	        $log->write_to_log_file(3, "Problem retrieving ID of default output_format. Statement not executed.");
    	        // Write verbose.
    	        $log->write_verbose_to_error_stack(NULL, $stmt->errorInfo());
    	    }
	    }
	    // Return.
	    return $r;
	}
	

}

?>