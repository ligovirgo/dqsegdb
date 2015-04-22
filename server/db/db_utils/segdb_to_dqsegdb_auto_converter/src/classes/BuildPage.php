<?php
/*
DQSEGDB - Convert segdb-format data to DQSEGDB.
*/

// Get libraries.
require_once 'DAO.php';

// Page builder class.
class BuildPage {

	private $document;
 
	public function __construct()
	{
		// Set start time.
		$start_time = time();
		// Instantiate.
		$dao = new DAO();
		// Undertake update.
		$dao->run_conversion();
		// Set stop time and duration.
		$stop_time = time();
		$duration = $stop_time-$start_time;
	}
}

?>