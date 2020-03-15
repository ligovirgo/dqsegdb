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