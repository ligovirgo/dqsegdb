<?php
/*
DQSEGDB - Check for duplicate flags in the database, taking into account the underscore as wildcard character.
*/

// Get libraries.
require_once 'FlagCheck.php';

// Page builder class.
class BuildPage {

	private $document;
 
	public function __construct()
	{
		// Instantiate.
		$flagcheck = new FlagCheck();
		// Undertake update.
		$flagcheck->run_check();
	}
}

?>