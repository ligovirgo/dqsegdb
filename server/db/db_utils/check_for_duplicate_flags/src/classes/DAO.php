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
DQSEGDB - Check for duplicate flags in the database, taking into account the underscore as wildcard character.
*/

// Get libraries.
require_once 'Constants.php';
require_once 'Logger.php';

// Data Access Object class.
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
		// Get DB connection constants.
		$constant->db_connection_constants();
		// If connection not made.
		if(!$this->pdo) {
			// Create new PDO object for DQSEGDB.
			$this->pdo = new PDO("mysql:host=".$constant->host.";dbname=".$constant->db, $constant->db_user, $constant->db_pass);
			// If PDO object not set.
			if(!isset($this->pdo)) {
				// Write to log.
				$log->write_to_log("Unable to connect to database: ".$stmt->errorInfo());
				exit();
			}
		}
	}
	
	/* Get full ifo + flag array. */
	public function get_ifo_flag_array() {
		// Init.
		$a = array();
		// Instantiate.
		$log = new Logger();
		// Get DB cursor.
		$this->db_connect();
		// Build prepared statement.
		if(($stmt = $this->pdo->prepare("SELECT dq_flag_id, value_txt, dq_flag_name
										 FROM tbl_dq_flags
										 LEFT JOIN tbl_values ON tbl_dq_flags.dq_flag_ifo = tbl_values.value_id
										 ORDER BY value_txt, dq_flag_name"))) {
			// If statement executes.
			if($stmt->execute()) {
				// Bind by column name.
				$stmt->bindColumn('dq_flag_id', $dq_flag_id);
				$stmt->bindColumn('value_txt', $ifo);
				$stmt->bindColumn('dq_flag_name', $dq_flag_name);
				// Loop.
				while($stmt->fetch()) {
					// Push flag to array.
					$a[$dq_flag_id] = array('ifo' => $ifo, 'dq_flag_name' => $dq_flag_name);
				}
			}
			// Otherwise.
			else {
				// Write to log.
				$log->write_to_log("Problem retrieving concatenated IFO-Flags: ".$stmt->errorInfo());
			}
		}
		// Return.
		return $a;
	}
	
	/* Get flag name. */
	public function get_flag_name($id) {
		// Init.
		$r = NULL;
		// Instantiate.
		$log = new Logger();
		// Get DB cursor.
		$this->db_connect();
		// Build prepared statement.
		if(($stmt = $this->pdo->prepare("SELECT value_txt, dq_flag_name
										 FROM tbl_dq_flags
										 LEFT JOIN tbl_values ON tbl_dq_flags.dq_flag_ifo = tbl_values.value_id
										 WHERE dq_flag_id=:id"))) {
			// If statement executes.
			if($stmt->execute(array(':id' => $id))) {
				// Bind by column name.
				$stmt->bindColumn('value_txt', $ifo);
				$stmt->bindColumn('dq_flag_name', $dq_flag_name);
				// Loop.
				while($stmt->fetch()) {
					// Push flag to array.
					$r = $ifo.':'.$dq_flag_name;
				}
			}
			// Otherwise.
			else {
				// Write to log.
				$log->write_to_log("Problem retrieving flag name for ID=".$id.": ".$stmt->errorInfo());
			}
		}
		// Return.
		return $r;
	}

	/* Get flag versions. */
	public function get_flag_versions($id) {
		// Init.
		$a = array();
		// Instantiate.
		$log = new Logger();
		// Get DB cursor.
		$this->db_connect();
		// Build prepared statement.
		if(($stmt = $this->pdo->prepare("SELECT dq_flag_version_id, dq_flag_version
										 FROM tbl_dq_flag_versions
										 WHERE dq_flag_fk=:id"))) {
			// If statement executes.
			if($stmt->execute(array(':id' => $id))) {
				// Bind by column name.
				$stmt->bindColumn('dq_flag_version_id', $dq_flag_version_id);
				$stmt->bindColumn('dq_flag_version', $dq_flag_version);
				// Loop.
				while($stmt->fetch()) {
					// Add to array.
					$a[$dq_flag_version_id] = $dq_flag_version;
				}
			}
			// Otherwise.
			else {
				// Write to log.
				$log->write_to_log("Problem retrieving flag versions for ID=".$id.": ".$stmt->errorInfo());
			}
		}
		// Return.
		return $a;
	}
	
	/* Update bad flag name. */
	public function update_bad_flag_name($id) {
		// Init.
		$r = FALSE;
		// Instantiate.
		$log = new Logger();
		// Write to log.
		$log->write_to_log("Updating bad flag name...");
		// Get DB cursor.
		$this->db_connect();
		// Build prepared statement.
		if(($stmt = $this->pdo->prepare("UPDATE tbl_dq_flags
										 SET dq_flag_name=CONCAT(dq_flag_name, '_DUPLICATE_NAME')
										 WHERE dq_flag_id=:id"))) {
			// If statement executes.
			if($stmt->execute(array(':id' => $id))) {
				// Write to log.
				$log->write_to_log("Bad flag name updated.");
				// Set.
				$r = TRUE;
			}
			// Otherwise.
			else {
				// Write to log.
				$log->write_to_log("Problem updating bad flag name: ".$stmt->errorInfo());
			}
		}
		// Return.
		return $r;
	}
	
	/* Update flag version metadata. */
	public function update_flag_version_metadata($good_flag_version_id, $bad_flag_version_id) {
		// Init.
		$r = FALSE;
		// Instantiate.
		$log = new Logger();
		// Write to log.
		$log->write_to_log("Updating flag version metadata...");
		// Get DB cursor.
		$this->db_connect();
		
		// Write to log.
		$log->write_to_log("UPDATE tbl_dq_flag_versions v
										 INNER JOIN 
										 (
										   SELECT
										   ".$good_flag_version_id." AS 'version_id',
										   SUM(dq_flag_version_known_segment_total) AS 'known_tot',
										   MIN(dq_flag_version_known_earliest_segment_time) AS 'known_earliest',
										   MAX(dq_flag_version_known_latest_segment_time) AS 'known_latest',
										   SUM(dq_flag_version_active_segment_total) AS 'active_tot',
										   MIN(dq_flag_version_active_earliest_segment_time) AS 'active_earliest',
										   MAX(dq_flag_version_active_latest_segment_time) AS 'active_latest',
										   MIN(dq_flag_version_date_created) AS 'date_created',
										   MIN(dq_flag_version_date_last_modified) AS 'last_modified'
										   FROM tbl_dq_flag_versions
										   WHERE dq_flag_version_id=".$good_flag_version_id." OR dq_flag_version_id=".$bad_flag_version_id."
										 ) s
										 ON v.dq_flag_version_id = s.version_id
										 SET v.dq_flag_version_known_segment_total = s.known_tot,
											 v.dq_flag_version_known_earliest_segment_time = s.known_earliest,
											 v.dq_flag_version_known_latest_segment_time = s.known_latest,
											 v.dq_flag_version_active_segment_total = s.active_tot,
											 v.dq_flag_version_active_earliest_segment_time = s.active_earliest,
											 v.dq_flag_version_active_latest_segment_time = s.active_latest,
											 v.dq_flag_version_date_created = s.date_created,
											 v.dq_flag_version_date_last_modified = s.last_modified
										 WHERE dq_flag_version_id=".$good_flag_version_id);
		
		// Build prepared statement.
		if(($stmt = $this->pdo->prepare("UPDATE tbl_dq_flag_versions v
										 INNER JOIN 
										 (
										   SELECT
										   ".$good_flag_version_id." AS 'version_id',
										   SUM(dq_flag_version_known_segment_total) AS 'known_tot',
										   MIN(dq_flag_version_known_earliest_segment_time) AS 'known_earliest',
										   MAX(dq_flag_version_known_latest_segment_time) AS 'known_latest',
										   SUM(dq_flag_version_active_segment_total) AS 'active_tot',
										   MIN(dq_flag_version_active_earliest_segment_time) AS 'active_earliest',
										   MAX(dq_flag_version_active_latest_segment_time) AS 'active_latest',
										   MIN(dq_flag_version_date_created) AS 'date_created',
										   MIN(dq_flag_version_date_last_modified) AS 'last_modified'
										   FROM tbl_dq_flag_versions
										   WHERE dq_flag_version_id=:g OR dq_flag_version_id=:b
										 ) s
										 ON v.dq_flag_version_id = s.version_id
										 SET v.dq_flag_version_known_segment_total = s.known_tot,
											 v.dq_flag_version_known_earliest_segment_time = s.known_earliest,
											 v.dq_flag_version_known_latest_segment_time = s.known_latest,
											 v.dq_flag_version_active_segment_total = s.active_tot,
											 v.dq_flag_version_active_earliest_segment_time = s.active_earliest,
											 v.dq_flag_version_active_latest_segment_time = s.active_latest,
											 v.dq_flag_version_date_created = s.date_created,
											 v.dq_flag_version_date_last_modified = s.last_modified
										 WHERE dq_flag_version_id=:g"))) {
			// If statement executes.
			if($stmt->execute(array(':g' => $good_flag_version_id, ':b' => $bad_flag_version_id))) {
				// Write to log.
				$log->write_to_log("Flag version metadata updated.");
				// Set.
				$r = TRUE;
			}
			// Otherwise.
			else {
				// Write to log.
				$log->write_to_log("Problem updating flag version metadata: ".$stmt->errorInfo());
			}
		}
		// Return.
		return $r;
	}
	
	/* Update flag version last modifier. */
	public function update_flag_version_last_modifier($good_flag_version_id, $bad_flag_version_id) {
		// Init.
		$r = FALSE;
		// Instantiate.
		$log = new Logger();
		// Write to log.
		$log->write_to_log("Updating flag version last modifier...");
		// Get DB cursor.
		$this->db_connect();
		// Build prepared statement.
		if(($stmt = $this->pdo->prepare("UPDATE tbl_dq_flag_versions v
										 INNER JOIN
										 (
										   SELECT ".$good_flag_version_id." AS 'version_id', dq_flag_version_last_modifier
										   FROM tbl_dq_flag_versions
										   WHERE dq_flag_version_id=:g OR dq_flag_version_id=:b
										   ORDER BY dq_flag_version_date_created DESC
										   LIMIT 1
										 ) s
										 ON v.dq_flag_version_id = s.version_id
										 SET v.dq_flag_version_last_modifier = s.dq_flag_version_last_modifier
										 WHERE dq_flag_version_id=:g"))) {
			// If statement executes.
			if($stmt->execute(array(':b' => $bad_flag_version_id, ':g' => $good_flag_version_id))) {
				// Write to log.
				$log->write_to_log("Flag version last modifier updated.");
				// Set.
				$r = TRUE;
			}
			// Otherwise.
			else {
				// Write to log.
				$log->write_to_log("Problem updating flag version last modifier: ".$stmt->errorInfo());
			}
		}
		// Return.
		return $r;
	}
	
	/* Update process table. */
	public function update_process_table($good_flag_version_id, $bad_flag_version_id) {
		// Init.
		$r = FALSE;
		// Instantiate.
		$log = new Logger();
		// Write to log.
		$log->write_to_log("Updating process table...");
		// Get DB cursor.
		$this->db_connect();
		// Build prepared statement.
		if(($stmt = $this->pdo->prepare("INSERT INTO tbl_processes
										 (dq_flag_version_fk,
										  process_full_name,
										  pid,
										  fqdn,
										  process_args,
										  process_comment,
										  user_fk,
										  insertion_time,
										  affected_active_data_segment_total,
										  affected_active_data_start,
										  affected_active_data_stop,
										  affected_known_data_segment_total,
										  affected_known_data_start,
										  affected_known_data_stop,
										  process_time_started,
										  process_time_last_used
										 )
										 SELECT ".$good_flag_version_id.",
												  process_full_name,
												  pid,
												  fqdn,
												  process_args,
												  process_comment,
												  user_fk,
												  insertion_time,
												  affected_active_data_segment_total,
												  affected_active_data_start,
												  affected_active_data_stop,
												  affected_known_data_segment_total,
												  affected_known_data_start,
												  affected_known_data_stop,
												  process_time_started,
												  process_time_last_used
										 FROM tbl_processes
										 WHERE dq_flag_version_fk=:b"))) {
			// If statement executes.
			if($stmt->execute(array(':b' => $bad_flag_version_id))) {
				// Write to log.
				$log->write_to_log("Process table updated.");
				// Set.
				$r = TRUE;
			}
			// Otherwise.
			else {
				// Write to log.
				$log->write_to_log("Problem updating process table: ".$stmt->errorInfo());
			}
		}
		// Return.
		return $r;
	}
	
	/* Update segments table. */
	public function update_segments_table($good_flag_version_id, $bad_flag_version_id) {
		// Init.
		$r = FALSE;
		// Instantiate.
		$log = new Logger();
		// Write to log.
		$log->write_to_log("Updating segments table...");
		// Get DB cursor.
		$this->db_connect();
		// Build prepared statement.
		if(($stmt = $this->pdo->prepare("INSERT INTO tbl_segments
										 (dq_flag_version_fk, segment_start_time, segment_stop_time)
										 SELECT ".$good_flag_version_id.", segment_start_time, segment_stop_time
										 FROM tbl_segments
										 WHERE dq_flag_version_fk=:b"))) {
					// If statement executes.
			if($stmt->execute(array(':b' => $bad_flag_version_id))) {
				// Write to log.
				$log->write_to_log("Segments table updated.");
				// Set.
				$r = TRUE;
			}
			// Otherwise.
			else {
				// Write to log.
				$log->write_to_log("Problem updating segments table: ".$stmt->errorInfo());
			}
		}
		// Return.
		return $r;
	}
	
	/* Update segment summarys table. */
	public function update_segment_summary_table($good_flag_version_id, $bad_flag_version_id) {
		// Init.
		$r = FALSE;
		// Instantiate.
		$log = new Logger();
		// Write to log.
		$log->write_to_log("Updating segment summary table...");
		// Get DB cursor.
		$this->db_connect();
		// Build prepared statement.
		if(($stmt = $this->pdo->prepare("INSERT INTO tbl_segment_summary
										 (dq_flag_version_fk, segment_start_time, segment_stop_time)
										 SELECT ".$good_flag_version_id.", segment_start_time, segment_stop_time
										 FROM tbl_segment_summary
										 WHERE dq_flag_version_fk=:b"))) {
			// If statement executes.
			if($stmt->execute(array(':b' => $bad_flag_version_id))) {
				// Write to log.
				$log->write_to_log("Segment summary table updated.");
				// Set.
				$r = TRUE;
			}
			// Otherwise.
			else {
				// Write to log.
				$log->write_to_log("Problem updating segment summary table: ".$stmt->errorInfo());
			}
		}
		// Return.
		return $r;
	}
}

?>