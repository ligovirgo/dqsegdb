<?php

//////////////////////////////
// Jquery-related actions. //
////////////////////////////

// Get libraries.
require_once('DAO.php');
require_once('GetServerData.php');
require_once('GetStructure.php');
require_once('InitVar.php');

// JavaScript/AJAX/Jquery action class.
class JSAction {
	
	private $document;
	private $getReqResponse;
 
	public function __construct() {
		// Build JS action response.
		$this->document = $this->getReqResponse();
	}

	// Decide which response to build.
	private function getReqResponse() {
		// Instantiate.
		$dao = new DAO();
		$serverdata = new GetServerData();
		$structure = new GetStructure();
		$variable = new Variables();
		// Get admin type.
		$variable->getReq();
			// Get query server form.
		if($variable->req == 'update_div_query_server') {
			// If IFO passed.
			if(isset($_GET['ifo'])) {
				$_SESSION['ifo'] = $_GET['ifo'];
				// Reset arrays.
				unset($_SESSION['uri_deselected']);
				$_SESSION['uri_deselected'] = array();
				unset($_SESSION['dq_flag']);
//				$_SESSION['dq_flag'] = array();
			}
			$serverdata->get_query_form_div(3);
			$this->document = $serverdata->query_form;
		}
		// Build an individual JSON payload.
		elseif($variable->req == 'build_individual_json_payload') {
			// Get file-related variables.
			$variable->get_file_related_variables();
			// Reset arrays.
			unset($_SESSION['uri_deselected']);
			$_SESSION['uri_deselected'] = array();
			// Add to deselected array.
			array_push($_SESSION['uri_deselected'], $_GET['uri']);
			// Get segment JSON.
			$data = $serverdata->retrieve_segments(NULL, NULL);
			// If JSON passed.
			if(!empty($data)) {
				// Set filename.
				$f = time().'.json';
				// If put to file successful.
				if(file_put_contents($variable->doc_root.$variable->download_dir.$f, $data)) {
					// Insert file metadata to database.
					$dao->insert_file_metadata($f);
					// Set return.
					$this->document = $variable->download_dir.$f;
				}
			}
		}
		// Update version div.
		elseif($variable->req == 'update_version_div') {
			// If flag passed.
			if(isset($_GET['dq_flag'])) {
				$_SESSION['dq_flag'] = $_GET['dq_flag'];
			}
			$serverdata->get_version_div_contents(3);
			$this->document = $serverdata->version_div;
		}
		// Update version div from textarea.
		elseif($variable->req == 'update_version_div_from_ta') {
			// If flags passed.
			if(isset($_GET['dq_flag'])) {
				// Set flag session.
				$_SESSION['dq_flag'] = $serverdata->set_ta_flags($_GET['dq_flag']);
			}
			$serverdata->get_version_div_contents(3);
			$this->document = $serverdata->version_div;
		}
		// Get version div.
		elseif($variable->req == 'update_version_select_session') {
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
		elseif($variable->req == 'deselect_version_uri') {
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
		// If retrieving segments.
		elseif($variable->req == 'retrieve_segments') {
			// Get file-related variables.
			$variable->get_file_related_variables();
			// Get segment JSON.
			$data = $serverdata->retrieve_segments($_GET['s'], $_GET['e']);
			// If JSON passed.
			if(!empty($data)) {
				// Set filename.
				$f = time().'.json';
				// If put to file successful.
				if(file_put_contents($variable->doc_root.$variable->download_dir.$f, $data)) {
					// Insert file metadata to database.
					$dao->insert_file_metadata($f);
				}
			}
		}
		// If re-populating recent query results div.
		elseif($variable->req == 'get_recent_query_results') {
			$this->document = $dao->get_recent_query_results(3);
		}
		// If providing option to change host.
		elseif($variable->req == 'get_current_host_box') {
			// Update session to take request into account.
			if(!$_SESSION['changing_current_host']) {
				$_SESSION['changing_current_host'] = TRUE;
			}
			else {
				$_SESSION['changing_current_host'] = FALSE;
			}
			// Get current-host div contents.
			$this->document = $structure->get_current_host_div_contents(3);
		}
		// Set the currently-used host.
		elseif($variable->req == 'set_current_host') {
			$_SESSION['default_host'] = $_GET['h'];
			// Unset selected flags.
			unset($_SESSION['dq_flag']);
			// Unset selected URI.
			unset($_SESSION['uri_deselected']);
			// Stop changing host.
			$_SESSION['changing_current_host'] = FALSE;
		}
		// Alternate the flag choice option.
		elseif($variable->req == 'alternate_flag_choice_option') {
			if($_SESSION['flag_choice_option'] == 0) {
				$_SESSION['flag_choice_option'] = 1;
			}
			else {
				$_SESSION['flag_choice_option'] = 0;
			}
			// Get currently selected option.
			$this->document = $serverdata->get_choose_flag_option(3);
		}
		
		// Output response.
		echo $this->document;
	}

}

?>