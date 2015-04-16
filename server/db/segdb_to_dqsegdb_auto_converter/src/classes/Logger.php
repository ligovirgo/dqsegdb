<?php
/*
DQSEGDB - Convert segdb-format data to DQSEGDB.
Logger class.
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