<?php

/*****************************
 * DQSEGDB Log-file analyser *
* *************************/

/* Get libraries. */
require_once('Constants.php');

/* Logger class. */
class Logger {
	
	// Write to log file function.
	public function write_to_log_file($l, $info) {
		// Instantiate.
		$constant = new Constants();
		// Get constants.
		$constant->logger_constants();
		// Get log levels.
		$a = $constant->log_levels;
		// If level passed is equal to or greater than the log level set.
		if($l >= $constant->log_current_level) {
			// Output to log file.
			file_put_contents($constant->log_dir.'/'.date('Y-m-d').'.log', date('Y-m-d H:i:s').' - '.$a[$l].' - '.$info."\n",  FILE_APPEND);
		}
	}
	
	// Write verbose details to error stack.
	public function write_verbose_to_error_stack($info, $array) {
		// Init.
		$str = NULL;
		// Instantiate.
		$constant = new Constants();
		// Get constants.
		$constant->logger_constants();
		// If verbose is set.
		if($constant->log_verbose) {
			// If code passed.
			if(isset($code)) {
				$str .= $code.' - ';
			}
			// If info passed.
			if(isset($info)) {
				$str .= $info.' - ';
			}
			// If array passed.
			if(isset($array) && is_array($array)) {
				// Loop array.
				foreach($array as $key => $val) {
					$str .= $val.' - ';
				}
			}
			// If string has been set.
			if(!empty($str)) {
				// Remove last three characters from string.
				$str = substr($str, 0, -3);
				// Output to log file.
				file_put_contents($constant->log_dir.'/'.date('Y-m-d').'.log', date('Y-m-d H:i:s').' - VERBOSE DETAILS - '.$str."\n",  FILE_APPEND);
			}
		}
	}
	
	
}

?>