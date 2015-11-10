<?php

// Get libraries.
require_once('Constants.php');
require_once('GetStructure.php');

// Page content class.
class GetLogFile {

	// Get log file analysis.
	public function get_log_file_analysis($tabs) {
		// Init.
		$str = NULL;
		$dir = 'data/analyse';	// Log file directory to be read.
		$csv_of = 'output/dqsegdb5_error_log_20150218.csv';	// Produced CSV output file.
		$min_rs = 0;
		// Ensure output files of the same name are removed, otherwise append will add to them.
		$this->remove_output_files($csv_of);
		// Get logged attempt requests.
		$str .= $this->get_logged_attempt_requests($dir, $csv_of, 'csv', $tabs);
		// Get response times.
//		$str .= $this->get_response_times($dir, $csv_of, 'csv', $min_rs, $tabs);	// Data directory, CSV output file, CSV or HTML, minimum response time, HTML tabs.
		// Return.
		return $str;
	}
	
	// Remove existing output files of the same name.
	private function remove_output_files($csv_of) {
		// If output file passed.
		if(!empty($csv_of)) {
			// Remove.
			unlink($csv_of);
		}
	}
	
	// Get logged Attempt requests.
	private function get_logged_attempt_requests($dir, $csv_of, $mode, $tabs) {
		// Init.
		$str = NULL;
		$r = 0;						// Time in seconds counter.
		$tot_get = 0;				// Total GETs in a second.
		$tot_patch = 0;				// Total PATCHes in a second.
		$tot_put = 0;				// Total PUTs in a second.
		// Instantiate.
		$constant = new Constants();
		$structure = new GetStructure();
		// Get required tabs.
		$structure->get_required_tabs($tabs);
		// Get background constants.
		$constant->get_bg_constants();
		// If mode set to HTML.
		if($mode == 'html') {
			// Set header.
			$structure->get_header();
			$str .= $structure->hdr;
			// Output header.
			$str .= $structure->tab_str."<p>1. Reading Attempts made from log-file directory".$dir."/</p>\n";
		}
		// Otherwise, if CSV.
		elseif($mode == 'csv') {
			// Append to file.
			file_put_contents($csv_of, "DATE/TIME,LOG ENTRIES/s,GET/s,PATCH/s,PUT/s\n", FILE_APPEND);		}
		// Open data dir and read contents.
		foreach(scandir($dir) as $f) {
			// Output reading header.
			echo "READING: ".$dir."/".$f."\n";
			// Read log file.
			$f_c = file_get_contents($dir."/".$f);
			// Explode log file contents by line.
			$a = explode("\n", $f_c);
			// Loop array.
			foreach($a as $ln => $lv) {
				// Explode by space.
				$l_a = explode(' ', $lv);
				// If attempt handle available.
				if(!empty($l_a[10])) {
					// Only handle attempts made.
					if($l_a[10] == 'Attempt') {
						$date = str_replace(":", "", $l_a[6]);
						$time = substr(str_replace(":INFO:", "", str_replace(":INFO:GET", "", str_replace(":INFO:PATCH", "", $l_a[7]))), 0, -4);
						$time_in_s = $time[6].$time[7];
						// If previous time in seconds has not yet been set.
						if(empty($pre_time_in_s)) {
							// Set it now.
							$pre_date = $date;
							$pre_time = $time;
							$pre_time_in_s = $time_in_s;
						}
						// If time in seconds still the same as last loop.
						if($time_in_s == $pre_time_in_s) {
							$r++;
							// Increment totals.
							if(strpos($l_a[7], ':INFO:GET') !== false) {
								$tot_get++;
							}
							elseif(strpos($l_a[7], ':INFO:PATCH') !== false) {
								$tot_patch++;
							}
							elseif(strpos($l_a[7], ':INFO:PUT') !== false) {
								$tot_put++;
							}
						}
						// Otherwise.
						else {
							// Set backgrounds.
							$r_output = $r;
							$tot_get_output = $tot_get;
							$tot_put_output = $tot_put;
							$tot_patch_output = $tot_patch;
							// If mode set to HTML.
							if($mode == 'html') {
								// If warning.
								if($r > 9) {
									$r_output = "<font".$constant->bg_warning.">".$r."</font>";
								}
								if($tot_get > 9) {
									$tot_get_output = "<font".$constant->bg_warning.">".$tot_get."</font>";
								}
								if($tot_put > 9) {
									$tot_put_output = "<font".$constant->bg_warning.">".$tot_put."</font>";
								}
								if($tot_patch > 9) {
									$tot_patch_output = "<font".$constant->bg_warning.">".$tot_patch."</font>";
								}
								// Set for output.
								$str .= $structure->tab_str.$pre_date." - ".$pre_time." - Log entries/s: ".$r_output." (GET: ".$tot_get_output."; PATCH: ".$tot_patch_output."; PUT: ".$tot_put_output.")<br />\n";
							}
							// Otherwise, if mode set to CSV.
							elseif($mode == 'csv') {
								// Append to file.
								file_put_contents($csv_of, "\"*".$pre_date." ".$pre_time."\",".$r_output.",".$tot_get_output.",".$tot_patch_output.",".$tot_put_output."\n", FILE_APPEND);
							}
							// Reset seconds counter.
							$r = 1;
							// Reset totals.
							$tot_get = 0;
							$tot_patch = 0;
							$tot_put = 0;
							// Reset totals again, taking into account current loop.
							if(strpos($l_a[7], ':INFO:GET') !== false) {
								$tot_get++;
							}
							elseif(strpos($l_a[7], ':INFO:PATCH') !== false) {
								$tot_patch++;
							}
							elseif(strpos($l_a[7], ':INFO:PUT') !== false) {
								$tot_put++;
							}
						}
						// Set previous time in seconds.
						$pre_date = $date;
						$pre_time = $time;
						$pre_time_in_s = $time_in_s;
					}
				}
			}
		}
		// If HTML.
		if($mode == 'html') {
			// Get footer.
			$structure->get_footer();
			$str .= $structure->ftr;
		}
		// If CSV.
		elseif($mode == 'csv') {
			echo "OUTPUT FILE: ".$csv_of."\n";
		}
		// Return.
		return $str;
	}
	
	// Get response times - Data directory, CSV output file, CSV or HTML, minimum response time, HTML tabs.
	private function get_response_times($dir, $csv_of, $mode, $min_rs, $tabs) {
		// Init.
		$str = NULL;
		$a_o = array();		// Array of open requests ('Attempt made' without 'Completed successfully').
		// Instantiate.
		$constant = new Constants();
		$structure = new GetStructure();
		// Get required tabs.
		$structure->get_required_tabs($tabs);
		// Get background constants.
		$constant->get_bg_constants();
		// If mode set to HTML.
		if($mode == 'html') {
			// Set header.
			$structure->get_header();
			$str .= $structure->hdr;
			// Output header.
			$str .= $structure->tab_str."<p>2. Reading response times between 'Attempt made' and 'Successfully completed' from ".$dir."/</p>\n";
			// Output completed attempts
			$str .= $structure->tab_str."<p>Completed attempts:</p>\n";
			// Open table.
			$str .= $structure->tab_str."<table cellpadding=\"0\"  cellspacing=\"1\"  border=\"1\" width=\"100%\">\n";
			// Output headers.
			$str .= $structure->tab_str."	<tr>\n";
			$str .= $structure->tab_str."		<td>Request</td>\n";
			$str .= $structure->tab_str."		<td>Attempt made</td>\n";
			$str .= $structure->tab_str."		<td>Successfully completed</td>\n";
			$str .= $structure->tab_str."		<td>Response time (ms)</td>\n";
			$str .= $structure->tab_str."	</tr>\n";
		}
		// Open data dir and read contents.
		foreach(scandir($dir) as $f) {
			// Output reading header.
			echo "READING: ".$dir."/".$f."\n";
			// Read log file.
			$f_c = file_get_contents($dir."/".$f);
			// Explode log file contents by line.
			$a = explode("\n", $f_c);
			// Loop array.
			foreach($a as $ln => $lv) {
				// Explode by space.
				$l_a = explode(' ', $lv);
				// If date/time set.
				if(!empty($l_a[6])) {
					// Set date and time.
					$date = str_replace(":", "", $l_a[6]);
					// If time set.
					if(!empty($l_a[7])) {
						$time = substr(str_replace(":INFO:", "", str_replace(":INFO:GET", "", str_replace(":INFO:PATCH", "", $l_a[7]))), 0, -4);
						$ms = substr(str_replace(":INFO:", "", str_replace(":INFO:GET", "", str_replace(":INFO:PATCH", "", $l_a[7]))), -3);
						// Set method.
						$m_a = explode(":", strrev($l_a[7]));
						$m = strrev($m_a[0]);
						// If URI set.
						if(!empty($l_a[8])) {
							// Set URI.
							$uri = $m." ".$l_a[8];
							// If attempt handle available.
							if(!empty($l_a[10])) {
								// Only handle attempts made.
								if($l_a[10] == 'Attempt') {
									// Add to open array.
									$a_o[$uri] = $date." ".$time.",".$ms;
								}
								// Otherwise, handle successful completions.
								elseif($l_a[10] == 'Completed') {
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
										// If mode set to HTML.
										if($mode == 'html') {
											// Set background.
											if($response_time_w_ms > 30) {
												$response_time_w_ms_output = "<font".$constant->bg_warning.">".$response_time_w_ms."</font>";
											}
											if($response_time_w_ms > 60) {
												$response_time_w_ms_output = "<font".$constant->bg_error.">".$response_time_w_ms."</font>";
											}
											// Set rows.
											$str .= $structure->tab_str."	<tr>\n";
											$str .= $structure->tab_str."		<td>".$uri."</td>\n";
											$str .= $structure->tab_str."		<td>".$a_o[$uri]."</td>\n";
											$str .= $structure->tab_str."		<td>".$date." ".$time.".".$ms."</td>\n";
											$str .= $structure->tab_str."		<td>".$response_time_w_ms_output."</td>\n";
						//					$str .= $structure->tab_str.$uri." - Attempted: ".$a_o[$uri]." (".$unix_attempt_time_w_ms."); Completed: ".$date." ".$time.",".$ms." (".$unix_response_time_w_ms.") (Response time: ".$response_time_w_ms.")<br />\n";
											$str .= $structure->tab_str."	</tr>\n";
										}
										// Otherwise, if mode set to CSV, response time is at least error and not a near-simultaneous dual call.
										elseif($mode == 'csv') {
											if($response_time_w_ms > $min_rs && !empty($a_o[$uri])) {
												// Append to file.
												file_put_contents($csv_of, '"'.$uri.'","'.$a_o[$uri].'","'.$date." ".$time.".".$ms.'",'.$response_time_w_ms_output."\n", FILE_APPEND);
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
		// If mode set to HTML.
		if($mode == 'html') {
			// Close table.
	//		$str .= $structure->tab_str."</table>\n";
			// Output uncompleted attempts
			$str .= $structure->tab_str."<p>Un-completed attempts:</p>\n";
//			print_r($a_o);
			// Get footer.
			$structure->get_footer();
			$str .= $structure->ftr;
		}
		// If CSV.
		elseif($mode == 'csv') {
			echo "OUTPUT FILE: ".$csv_of."\n";
		}
		// Return.
		return $str;
	}
}

?>