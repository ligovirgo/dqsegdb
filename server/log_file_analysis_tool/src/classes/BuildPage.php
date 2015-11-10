<?php

// Get libraries.
require_once('GetStructure.php');

// Page builder class.
class BuildPage {

	private $document;
 
	public function __construct() {
		// Instantiate.
		$structure = new GetStructure();
		// Get header.
		$structure->get_body();
		// Build document.
		$this->document .= $structure->bdy;
		// Output.
		echo $this->document;
	}
}

?>