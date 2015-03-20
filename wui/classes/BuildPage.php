<?php

// Get libraries.
require_once('GetServerData.php');
require_once('GetStructure.php');
require_once('InitVar.php');

// Page builder class.
class BuildPage
{

	private $document;
 
	public function __construct()
	{
		// Instantiate.
		$variable = new Variables();
		$serverdata = new GetServerData();
		// Set content call ID.
		$variable->getContentCallID();
		// If on homepage.
		if($variable->c == 1) {
			// If the default host has not been set.
			if(!isset($_SESSION['default_host']) || empty($_SESSION['default_host'])) {
				// Set default host.
				$_SESSION['default_host'] = $serverdata->get_quickest_host();
			}
		}
		// Instantiate.
		$structure = new GetStructure();
		// Get header.
		$structure->getHeader();
		// Get header.
		$structure->getBody();
		// Get footer.
		$structure->getFooter();
		// Build document.
		$this->document = $structure->hdr;
		$this->document .= $structure->bdy;
		$this->document .= $structure->ftr;
		echo $this->document;
	}
}

?>
