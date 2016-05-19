<?php

/*****************************
* DQSEGDB Log-file analyser *
* *************************/

/* Get libraries. */
require_once 'Constants.php';
require_once 'DAO.php';

/* Log-file-handling class. */
class LogFileAnalyser {

	/* Get log file analysis. */
	public function get_log_file_analysis() {
		// Init.
		$str = NULL;
		// Ensure output files of the same name are removed, otherwise append will add to them.
		$this->remove_output_files();
		// Get logged attempt requests.
//		$str .= $this->get_logged_attempt_requests();
		// Get response times.
		$str .= $this->get_response_times();
		// Return.
		return $str;
	}
	
	/* Remove existing output files of the same name. */
	private function remove_output_files() {
		// Instantiate.
		$constant = new Constants();
		// Get file constants.
		$constant->get_file_constants();
		// If not writing to the database.
		if($constant->output_format != 'sql') {
			// If output file passed.
			if(!empty($constant->output_dir)) {
				// Remove.
				unlink($constant->output_dir);
			}
		}
	}
	
	/* Get logged Attempt requests. */
	private function get_logged_attempt_requests() {
		// Init.
		$str = NULL;
		$r = 0;						// Time in seconds counter.
		$tot_get = 0;				// Total GETs in a second.
		$tot_patch = 0;				// Total PATCHes in a second.
		$tot_put = 0;				// Total PUTs in a second.
		$attempt_time = 0;
		// Instantiate.
		$constant = new Constants();
		// Get background constants.
		$constant->get_bg_constants();
		// Get file constants.
		$constant->get_file_constants();
		// Append to file.
		file_put_contents($constant->output_dir, "# DATE/TIME,TOTAL ATTEMPTS/s,GET/s,PATCH/s,PUT/s;\n");
		// Init.
		$attempt_time_pre = 0;
		// Open data dir and read contents.
		foreach(scandir($constant->analyse_dir) as $f) {
			// Output reading header.
			echo "READING: ".$constant->analyse_dir."/".$f."\n";
			// Read log file.
			$f_c = file_get_contents($constant->analyse_dir."/".$f);
			// Explode log file contents by line.
			$a = explode("\n", $f_c);
			// Loop array.
			foreach($a as $ln => $lv) {
				// Explode by space.
				$l_a = explode(' ', $lv);
				// If the time is available.
				if(isset($l_a[1])) {
					// Set time in seconds.
					$attempt_time = strtotime($l_a[0].' '.substr($l_a[1], 0, 8));
					$attempt_time_output = $l_a[0].' '.substr($l_a[1], 0, 8);
					// If attempt handle available.
					if(!empty($l_a[4])) {
						// Only handle attempts made.
						if($l_a[4] == 'Attempt') {
							// Increment totals.
							if(strpos($l_a[1], ':GET') !== false) {
								$tot_get++;
							}
							elseif(strpos($l_a[1], ':PATCH') !== false) {
								$tot_patch++;
							}
							elseif(strpos($l_a[1], ':PUT') !== false) {
								$tot_put++;
							}
						}
					}
					// If the attempt time is different to the last attempt time.
					if($attempt_time != 0 && $attempt_time != $attempt_time_pre) {
						// If CSV.
						if($constant->output_format == 'csv') {
							// Append to file.
							file_put_contents($constant->output_dir, $attempt_time_output.",".($tot_get+$tot_patch+$tot_put).",".$tot_get.",".$tot_patch.",".$tot_put.";\n", FILE_APPEND);
						}
						// If SQL.
						elseif($constant->output_format == 'sql') {
							
						}
						// Reset the per-second totals.
						$tot_get = 0;
						$tot_put = 0;
						$tot_patch = 0;
					}
					// Set previous attempt time in seconds.
					$attempt_time_pre = $attempt_time;
				}
			}
		}
		// Set output file.
		echo "OUTPUT FILE: "." - ".$constant->output_dir."\n";
		// Return.
		return $str;
	}
	
	/* Get response times. */
	private function get_response_times() {
		// Init.
		$str = NULL;
		$a_o = array();		// Array of open requests ('Attempt made' without 'Completed successfully').
		// Instantiate.
		$constant = new Constants();
		$dao = new DAO();
		// Get file constants.
		$constant->get_file_constants();
		// Get time constants.
		$constant->get_time_constants();
		// If CSV.
		if($constant->output_format == 'csv') {
			// Create file.
			file_put_contents($constant->output_dir, "# METHOD, URI, DATE/TIME CALL, DATE/TIME REPLY, RESPONSE TIME (ms);\n");
		}
		// Open data dir and read contents.
		foreach(scandir($constant->analyse_dir) as $f) {
			// Output reading header.
			echo "READING: ".$constant->analyse_dir."/".$f."\n";
			// Read log file.
			$f_c = file_get_contents($constant->analyse_dir."/".$f);
			// Explode log file contents by line.
			$a = explode("\n", $f_c);
			// Loop array.
			foreach($a as $ln => $lv) {
				// Explode by space.
				$l_a = explode(' ', $lv);
				// If date/time set.
				if(!empty($l_a[0])) {
					// Set date and time.
					$date = $l_a[0];
					// If time set.
					if(!empty($l_a[1])) {
						$time = substr($l_a[1], 0, 8);
						$ms = substr($l_a[1], 9, 3);
						// Set method.
						$m_a = explode(":", strrev($l_a[1]));
						$m = strrev($m_a[0]);
						// If URI set.
						if(!empty($l_a[2])) {
							// Set URI.
							$uri = $m." ".$l_a[2];
							// If attempt handle available.
							if(!empty($l_a[4])) {
								// Only handle attempts made.
								if($l_a[4] == 'Attempt') {
									// Add to open array.
									$a_o[$uri] = $date." ".$time.",".$ms;
								}
								// Otherwise, handle successful completions.
								elseif($l_a[4] == 'Completed') {
									// If attempt recorded in array.
									if(!empty($a_o[$uri])) {
										// Calculate response time.
										$unix_attempt_time = strtotime(substr($a_o[$uri], 0, -4));
										$unix_attempt_time_w_ms = (float) $unix_attempt_time.".".substr($a_o[$uri], -3);
										$unix_response_time = strtotime($date." ".$time);
										$unix_response_time_w_ms = (float) $unix_response_time.".".$ms;
										$response_time = $unix_response_time - $unix_attempt_time;
										$response_time_w_ms = round($unix_response_time_w_ms - $unix_attempt_time_w_ms, 5);
										$response_time_w_ms_output = $response_time_w_ms;
										// Response time is at least error and not a near-simultaneous dual call.
										if($response_time_w_ms > $constant->minimum_response_time && !empty($a_o[$uri])) {
											// If CSV.
											if($constant->output_format == 'csv') {
												// Append to file.
												file_put_contents($constant->output_dir, '"'.$m.'","'.$l_a[2].'","'.$a_o[$uri].'","'.$date." ".$time.",".$ms.'",'.$response_time_w_ms_output.";\n", FILE_APPEND);
											}
											// If SQL.
											elseif($constant->output_format == 'sql') {
												// Insert to DB.
												$dao->insert_response_time($m, $l_a[2], $a_o[$uri], $date." ".$time.",".$ms, $response_time_w_ms_output);
											}
										}
										// Remove URI from open array.
										unset($a_o[$uri]);
									}
								}
							}
						}
					}
				}
			}
		}
		// If CSV.
		if($constant->output_format == 'csv') {
			// State output file.
			echo "OUTPUT FILE: ".$constant->output_dir."\n";
		}
		// Return.
		return $str;
	}
}

?>