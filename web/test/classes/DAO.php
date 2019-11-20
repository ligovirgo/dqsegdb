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
require_once 'APIRequests.php';
require_once 'Constants.php';
require_once 'Logger.php';
require_once 'User.php';
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
	
	/* Get the ID for an output-format. */
	public function get_output_format_id($of) {
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
							 			 WHERE output_format=:of")) {
			// Execute.
    	    if($stmt->execute(array(':of' => $of))) {
    	        // Bind by column name.
    	        $stmt->bindColumn('output_format_id', $output_format_id);
    	        // Loop.
    	        while($stmt->fetch()) {
    	            // Set.
    	            $r = $output_format_id;
    	        }
    	    }
    	    else {
    	        // Write to log.
    	        $log->write_to_log_file(3, "Problem retrieving ID for output-format: ".$of.". Statement not executed.");
    	        // Write verbose.
    	        $log->write_verbose_to_error_stack(NULL, $stmt->errorInfo());
    	    }
	    }
	    // Return.
	    return $r;
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
	
	///////////////////
	// FILE-RELATED //
	/////////////////
	
	/* Insert file metadata to database. */
	public function insert_file_metadata($f, $format) {
	    // Init.
	    $r = FALSE;
	    $fu = NULL;
	    // Instantiate.
	    $api = new APIRequests();
	    $constants = new Constants();
	    $log = new Logger();
	    $user = new User();
	    // Get file-related variables.
	    $constants->get_file_constants();
        // Get user ID for this user.
        $uid = $user->get_valid_user_id();
        // If valid UID is returned.
        if($uid != 0) {
            // Explode filename backwards.
            $exp = explode('.', $f);
            // Get file format ID.
            $of_id = $this->get_output_format_id($exp[1]);
            // Set args.
            $args = $api->get_uri_args($_SESSION['gps_start'], $_SESSION['gps_stop']);
            // Get filesize.
            $fs = filesize($constants->doc_root.$constants->download_dir.str_replace("_", ".", $f));
            // Loop through selected flags used in file creation and add to history.
            foreach($_SESSION['dq_flag_uris'] as $ifo_flag => $versions) {
                // Loop selected versions.
                foreach($versions as $kv => $v) {
                    // Build URI.
                    $uri = '/dq/'.str_replace('___', '/', $ifo_flag).'/'.$v;
                    // Build string.
                    $fu .= ', '.$uri.$args;
                }
            }
            // Remove first two characters from URI string.
            $fu = substr($fu, 2);
            // Create PDO object
            $this->db_connect();
            // Build prepared statement.
            if($stmt = $this->pdo->prepare("INSERT INTO tbl_file_metadata
			 		 					    (file_name, file_size, file_uri_used,
                                             file_format_fk, file_user_fk, file_host_fk)
								 			VALUES
											(:f, :fs, :fu,
                                            :format_id, :uid, :h)")) {
				// Execute.
	            if($stmt->execute(array(':f' => $f, ':fs' => $fs, ':fu' => $fu,
	                                    ':format_id' => $of_id, ':uid' => $uid,
	                                    ':h' => $_SESSION['host_id']))) {
	                // Set.
	                $r = TRUE;
	            }
	            else {
	                // Write to log.
	                $log->write_to_log_file(3, "Problem inserting metadata file: ".$f.". Statement not executed.");
	                // Write verbose.
	                $log->write_verbose_to_error_stack(NULL, $stmt->errorInfo());
	            }
            }
	    }
    	// Return.
	    return $r;
	}

	/* Get the ID of the file that the user has just built. */
	public function get_new_file_id() {
	    // Init.
	    $r = 0;
	    $file_id = 0;
	    // Instantiate.
	    $log = new Logger();
	    $user = new User();
	    // Get the user ID.
	    $uid = $user->get_valid_user_id();
	    // Create PDO object
	    $this->db_connect();
	    // Build prepared statement.
	    if($stmt = $this->pdo->prepare("SELECT file_id
										FROM tbl_file_metadata
										WHERE file_user_fk=:u
                                        ORDER BY file_id DESC
                                        LIMIT 1")) {
            // If statement executes.
	        if($stmt->execute(array(':u' => $uid))) {
    	        // Bind by column name.
    	        $stmt->bindColumn('file_id', $file_id);
    	        // Loop.
    	        while($stmt->fetch()) {
    	            // Set.
    	            $r = $file_id;
    	        }
    	    }
    	    // Otherwise.
    	    else {
    	        // Write to log.
    	        $log->write_to_log_file(3, "Problem retrieving ID for user: ".$uid.". Statement not executed.");
    	        // Write verbose.
    	        $log->write_verbose_to_error_stack(NULL, $stmt->errorInfo());
    	    }
	    }
	    // Return.
	    return $r;
	}
	
	/* Get an array of file details. */
	public function get_file_details($f) {
	    // Init.
	    $a = array();
	    // Instantiate.
	    $log = new Logger();
	    // Create PDO object
	    $this->db_connect();
	    // Build prepared statement.
	    if($stmt = $this->pdo->prepare("SELECT *
										FROM tbl_file_metadata
                                        WHERE file_id=:f")) {
			// If statement executes.
    	    if($stmt->execute(array(':f' => $f))) {
    	        // Fetch the result.
    	        $a = $stmt->fetchAll();
    	    }
    	    // Otherwise.
    	    else {
    	        // Write to log.
    	        $log->write_to_log_file(3, "Problem retrieving array of file details for ID: ".$f.". Statement not executed.");
    	        // Write verbose.
    	        $log->write_verbose_to_error_stack(NULL, $stmt->errorInfo());
    	    }
	    }
	    // Return.
	    return $a;
	}
	
	/////////////////////////////
	// USER-RELATED FUNCTIONS //
	///////////////////////////

	/* Get the ID for a user. */
	public function get_user_id($u) {
	    // Init.
	    $r = 0;
	    $user_id = 0;
	    // Instantiate.
	    $log = new Logger();
        // Create PDO object
        $this->db_connect();
        // Build prepared statement.
        if($stmt = $this->pdo->prepare("SELECT user_id
							 		     FROM tbl_users
							 			 WHERE user_name=:u")) {
		    // Execute.
	        if($stmt->execute(array(':u' => $u))) {
	            // Bind by column name.
	            $stmt->bindColumn('user_id', $user_id);
	            // Loop.
	            while($stmt->fetch()) {
	                // Set.
	                $r = $user_id;
	            }
	        }
	        else {
	            // Write to log.
	            $log->write_to_log_file(3, "Problem retrieving ID for user: ".$u.". Statement not executed.");
	            // Write verbose.
	            $log->write_verbose_to_error_stack(NULL, $stmt->errorInfo());
            }
	    }
	    // Return.
	    return $r;
	}
	    
	/* Get the username from an ID. */
	public function get_username($u) {
	    // Init.
	    $r = 0;
	    $user_name = 0;
	    // Instantiate.
	    $log = new Logger();
	    // Create PDO object
	    $this->db_connect();
	    // Build prepared statement.
	    if($stmt = $this->pdo->prepare("SELECT user_name
							 		     FROM tbl_users
							 			 WHERE user_id=:u")) {
			// Execute.
    	    if($stmt->execute(array(':u' => $u))) {
    	        // Bind by column name.
    	        $stmt->bindColumn('user_name', $user_name);
    	        // Loop.
    	        while($stmt->fetch()) {
    	            // Set.
    	            $r = $user_name;
    	        }
    	    }
    	    else {
    	        // Write to log.
    	        $log->write_to_log_file(3, "Problem retrieving name for user ID: ".$u.". Statement not executed.");
    	        // Write verbose.
    	        $log->write_verbose_to_error_stack(NULL, $stmt->errorInfo());
  	        }
        }
        // Return.
        return $r;
    }
	    
	/* Insert new user. */
	public function insert_user($u) {
	    // Init.
	    $r = FALSE;
        // If user does not already exist.
	    if($this->get_user_id($u) == 0) {
	        // Instantiate.
	        $log = new Logger();
	        // Create PDO object
	        $this->db_connect();
	        // Build prepared statement.
	        if($stmt = $this->pdo->prepare("INSERT INTO tbl_users
						 					 (user_name)
							 				 VALUES
											 (:u)")) {
				// Execute.
	            if($stmt->execute(array(':u' => $u))) {
	                // Set.
	                $r = TRUE;
	            }
	            else {
	                // Write to log.
	                $log->write_to_log_file(3, "Problem inserting user: ".$u.". Statement not executed.");
	                // Write verbose.
	                $log->write_verbose_to_error_stack(NULL, $stmt->errorInfo());
	            }
	        }
	    }
	    // Return.
	    return $r;
	}

}

?>