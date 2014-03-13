<?php

//////////////////////////////
// Jquery-related actions. //
////////////////////////////

// Get libraries.
require_once('DAO.php');
require_once('GetServerData.php');
require_once('InitVar.php');

// JavaScript/AJAX/Jquery action class.
class JSAction {
	private $document;
	private $getAdTypeResponse;
 
	public function __construct() {
		// Build JS action response.
		$this->document = $this->getAdTypeResponse();
	}

	// Decide which response to build.
	private function getAdTypeResponse()
	{
		// Instantiate.
		$serverdata = new GetServerData();
		$variable = new Variables();
		// Get admin type.
		$variable->getAdminType();
		// Get query server form.
		if($variable->ad_type == 'update_div_query_server') {
			// If IFO passed.
			if(isset($_GET['ifo'])) {
				$_SESSION['ifo'] = $_GET['ifo'];
			}
			$serverdata->get_query_form_div(3);
			$this->document = $serverdata->query_form;
		}
		// Get version div.
		if($variable->ad_type == 'update_version_div') {
			// If IFO passed.
			if(isset($_GET['dq_flag'])) {
				$_SESSION['dq_flag'] = $_GET['dq_flag'];
			}
			$serverdata->get_version_div_contents(3);
			$this->document = $serverdata->version_div;
		}
		// Get version div.
		if($variable->ad_type == 'update_version_select_session') {
			// If URI passed.
			if(isset($_GET['uri'])) {
				// If URI not in update array.
				if(!in_array($_GET['uri'], $_SESSION['dq_flag_version_update'])) {
					// Add to array.
					array_push($_SESSION['dq_flag_version_update'], $_GET['uri']);
				}
				// Otherwise.
				else {
					// Get value key and then delete.
					$k = array_search($_GET['uri'], $_SESSION['dq_flag_version_update']);
					unset($_SESSION['dq_flag_version_update'][$k]);
				}
			}
			$serverdata->get_flag_version_span_contents($_GET['uri']);
			$this->document = $serverdata->version_span;
		}
		// If selecting/de-selecting a version.
		if($variable->ad_type == 'deselect_version_uri') {
			// Set selected class to re-send.
			$this->document = 'span_version_no';
			// If URI passed.
			if(isset($_GET['uri'])) {
				// If URI not in deselected array.
				if(!in_array($_GET['uri'], $_SESSION['uri_deselected'])) {
					// Add to deselected array.
					array_push($_SESSION['uri_deselected'], $_GET['uri']);
					// Set deselected class to re-send.
					$this->document = 'span_version_no_deselected';
				}
				// Otherwise, if in deselected array.
				else {
					// Remove from de-selected array.
					if(($k = array_search($_GET['uri'], $_SESSION['uri_deselected'])) !== false) {
						unset($_SESSION['uri_deselected'][$k]);
					}
				}
			}
		}
		// Output response.
		echo $this->document;
	}
}

?>