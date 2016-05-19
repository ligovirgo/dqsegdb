<?php
/*
DQSEGDB - Check for duplicate flags in the database, taking into account the underscore as wildcard character.
*/

// Get libraries.
require_once 'Constants.php';
require_once 'DAO.php';
require_once 'Logger.php';

/* Flag Check Object class. */
class FlagCheck {	

	/* Run Check. */
	public function run_check() {
		// Init.
		$a_final = array();
		$a_duplicate = array();
		// Instantiate.
		$constant = new Constants();
		$dao = new DAO();
		$log = new Logger();
		// Get version constant.
		$constant->package_version_constants();
		// Log.
		$log->write_to_log("Starting DQSEGDB duplicate flag checker (version: ".$constant->package_version.")");
		// Get full ifo + flag array.
		$a = $dao->get_ifo_flag_array();
		// Log.
		$log->write_to_log("Looping ifo-flag array...");
		// Loop array.
		foreach($a as $dq_flag_id => $dq_flag_details) {
			// Strip to only alpha-numeric and set all as upper-case.
			$ifo_flag_fmt = strtolower($dq_flag_details['ifo'].'-'.preg_replace("/[^A-Za-z0-9]/", "", $dq_flag_details['dq_flag_name']));
			// If not already in final array.
			if(!in_array($ifo_flag_fmt, $a_final)) {
				// Push to array.
				$a_final[$dq_flag_id] = $ifo_flag_fmt;
				// Log.
				//$log->write_to_log("OK: ".$ifo_flag_fmt);
			}
			// Otherwise.
			else {
				// Log.
				//$log->write_to_log("DUPLICATE: ".$ifo_flag_fmt." duplicate of: ".$dq_flag_details['dq_flag_name']." (".$dq_flag_id.")");
				// Add to duplicate array.
				$a_duplicate[$dq_flag_id] = array_search($ifo_flag_fmt, $a_final);
			}
		}
		// If duplicates have been found.
		if(!empty($a_duplicate)) {
			// Handle duplicates.
			$this->handle_duplicates($a_duplicate);
		}
		// Otherwise.
		else {
			// Log.
			$log->write_to_log("No duplicate flags have been found.");
		}
		// Log.
		$log->write_to_log("DQSEGDB duplicate flag checker (version: ".$constant->package_version.") finished.");
	}
	
	/* Handle duplicates. */
	private function handle_duplicates($a) {
		// Instantiate.
		$constant = new Constants();
		$dao = new DAO();
		$log = new Logger();
		// Get flag constants.
		$constant->flag_constants();
		// Loop through the duplicate flag array.
		foreach($a as $flag_a_id => $flag_b_id) {
			// Get flag names.
			$flag_a_name = $dao->get_flag_name($flag_a_id);
			$flag_b_name = $dao->get_flag_name($flag_b_id);
			// Get flag versions for these flags.
			$flag_a_versions = $dao->get_flag_versions($flag_a_id);
			$flag_b_versions = $dao->get_flag_versions($flag_b_id);
			// Set flag versions for output.
			$flag_a_versions_output = $this->set_flag_versions_for_output($flag_a_versions);
			$flag_b_versions_output = $this->set_flag_versions_for_output($flag_b_versions);
			// Log.
			$log->write_to_log("DUPLICATE: ".$flag_a_name." (".$flag_a_id."); duplicate of ".$flag_b_name." (".$flag_b_id.").");
			$log->write_to_log($flag_a_name." versions: ".$flag_a_versions_output."; ".$flag_b_name." versions: ".$flag_b_versions_output.".");
			// Handle merging.
			$this->handle_merging($flag_a_id, $flag_a_name, $flag_a_versions, $flag_b_id, $flag_b_name, $flag_b_versions);
			$log->write_to_log("-----");
		}
		
	}

	/* Set flag a versions for output. */
	private function set_flag_versions_for_output($a) {
		// Init.
		$r = NULL;
		// Loop array.
		foreach($a as $version_id => $version) {
			// Set.
			$r .= " ".$version." (ID: ".$version_id."), ";
		}
		// Remove last two characters from string.
		$r = substr($r, 0, -2);
		// Return.
		return $r;
	}
	
	/* Handle merging of one flag into another. */
	private function handle_merging($flag_a_id, $flag_a_name, $flag_a_versions, $flag_b_id, $flag_b_name, $flag_b_versions) {
		// Instantiate.
		$constant = new Constants();
		$dao = new DAO();
		$log = new Logger();
		// Get flag constants.
		$constant->flag_constants();
		// If flags to receive merged data have been set.
		if(!empty($constant->flags_to_receive_merged_data)) {
			// If flag ID A in array.
			if(in_array($flag_a_id, $constant->flags_to_receive_merged_data)) {
				// Set ID to receive merged data.
				$good_flag_id = $flag_a_id;
				$good_flag_name = $flag_a_name;
				$good_flag_versions = $flag_a_versions;
				reset($good_flag_versions);
				$good_flag_version_id = key($good_flag_versions);
				// Set ID to give merged data.
				$bad_flag_id = $flag_b_id;
				$bad_flag_name = $flag_b_name;
				$bad_flag_versions = $flag_b_versions;
				$bad_flag_version_id = reset($bad_flag_versions);
				reset($bad_flag_versions);
				$bad_flag_version_id = key($bad_flag_versions);
			}
			// Otherwise, if flag ID B in array.
			if(in_array($flag_b_id, $constant->flags_to_receive_merged_data)) {
				// Set ID to receive merged data.
				$good_flag_id = $flag_b_id;
				$good_flag_name = $flag_b_name;
				$good_flag_versions = $flag_b_versions;
				reset($good_flag_versions);
				$good_flag_version_id = key($good_flag_versions);
				// Set ID to give merged data.
				$bad_flag_id = $flag_a_id;
				$bad_flag_name = $flag_a_name;
				$bad_flag_versions = $flag_a_versions;
				reset($bad_flag_versions);
				$bad_flag_version_id = key($bad_flag_versions);
			}
			// If a good flag ID has not been set.
			if(!isset($good_flag_id)) {
				// Log.
				$log->write_to_log("No instructions have been manually passed to handle these flags.");
			}
			// Otherwise, if a good flag ID has been set.
			else {
				// Log.
				$log->write_to_log("Merging ".$bad_flag_name." (".$bad_flag_id.") into ".$good_flag_name." (".$good_flag_id.")...");
				// Update bad flag name.
				if($dao->update_bad_flag_name($bad_flag_id)) {
					// Update flag version last modifier.
					if($dao->update_flag_version_last_modifier($good_flag_version_id, $bad_flag_version_id)) {
						// Update flag version metadata.
						if($dao->update_flag_version_metadata($good_flag_version_id, $bad_flag_version_id)) {
							// Update process table.
							if($dao->update_process_table($good_flag_version_id, $bad_flag_version_id)) {
								// Update segments table.
								if($dao->update_segments_table($good_flag_version_id, $bad_flag_version_id)) {
									// Update segment summary table.
									if($dao->update_segment_summary_table($good_flag_version_id, $bad_flag_version_id)) {
										// Log.
										$log->write_to_log("Duplicate flag '".$bad_flag_name."', successfully merged into '".$good_flag_name."'.");
									}
								}
							}
						}
					}
				}
			}
		}
	}
}

?>