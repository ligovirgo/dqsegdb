<?php

// Get libraries.
require_once('LogFileAnalyser.php');

// Page builder class.
class BuildPage {

	private $document;
 
	public function __construct() {
		// Instantiate.
		$logfile = new LogFileAnalyser();
		// Get log file analysis.
		$logfile->get_log_file_analysis();
	}
}

?>