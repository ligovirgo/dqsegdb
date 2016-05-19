<?php
/*
DQSEGDB - Check for duplicate flags in the database, taking into account the underscore as wildcard character.
*/

// Logger class.
class Logger {
	
	// Write to log file function.
	public function write_to_log($m) {
		// Output to log file.
		echo date('d-m-y H:i:s')." - ".$m."\n";
	}

}

?>