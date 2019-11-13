<?php
/*
This file is part of the DQSEGDB WUI.

This file was written by Gary Hemming <gary.hemming@ego-gw.it>.

DQSEGDB WUI uses the following open source software:
- jQuery JavaScript Library v1.12.4, available under the MIT licence - http://jquery.org/license - Copyright jQuery Foundation and other contributors.
- W3.CSS by Jan Egil and Borge Refsnes.
- Font Awesome by Dave Gandy - http://fontawesome.io.
- Jquery Timepicker, developed and maintained by Willington Vega. Code licensed under the MIT and GPL licenses - http://timepicker.co
*/

// Get libraries.
require_once 'APIRequests.php';
require_once 'Homepage.php';
require_once 'SessionManager.php';

//////////////////////////////
// Jquery-related actions. //
////////////////////////////

/* JavaScript/AJAX/Jquery action class. */
class JSAction {
	
	private $document;
 
	/* Constructor. */
	public function __construct() {
		// Build JS action response.
		$this->document = $this->get_action();
	}

	/* Decide which response to build. */
	private function get_action() {
		// Init.
		$this->document = 0;
		// Initialise.
		$api = new APIRequests();
		$home = new Homepage();
		$session = new SessionManager();
		
		////////////////
		// HOST CALLS //
		////////////////
		
		if($_GET['action'] == 'check_host_connection') {
			// Convert response from boolean to integer.
		    $this->document = +$api->host_connection_available();
		}
		elseif($_GET['action'] == 'build_get_segments_form') {
		    $home->build_get_segments_form();
		    $this->document = $home->get_segments_form;
		}
		elseif($_GET['action'] == 'set_output_format') {
		    $_SESSION['output_format'] = $_GET['f'];
		}
		elseif($_GET['action'] == 'set_include_history') {
		    $_SESSION['include_history'] = $_GET['ih'];
		}
		elseif($_GET['action'] == 'switch_choose_flag_option') {
		    if($_SESSION['choose_flag_option'] == 0) {
    		    $_SESSION['choose_flag_option'] = 1;
		    }
		    elseif($_SESSION['choose_flag_option'] == 1) {
		        $_SESSION['choose_flag_option'] = 0;
		    }
		    $home->build_choose_flag_option();
		    $this->document = $home->choose_flag_option;
		}
		elseif($_GET['action'] == 'update_version_div') {
		    // If flag passed.
		    if(isset($_GET['dq_flag'])) {
		        $_SESSION['dq_flag'] = $_GET['dq_flag'];
		    }
		    $home->get_versions();
		    $this->document = $home->version_div;
		}
		elseif($_GET['action'] == 'update_version_div_from_ta') {
		    // If flags passed.
		    if(isset($_GET['dq_flag'])) {
		        // Set flag session.
		        $_SESSION['dq_flag'] = $home->set_ta_flags($_GET['dq_flag']);
		    }
		    $home->get_versions();
		    $this->document = $home->version_div;
		}
		elseif($_GET['action'] == 'select_version_uri') {
		    // If URI passed.
		    if(isset($_GET['uri'])) {
		        // If URI not in deselected array.
		        if(!in_array($_GET['uri'], $_SESSION['uri_selected'])) {
		            // Add to deselected array.
		            array_push($_SESSION['uri_selected'], $_GET['uri']);
		        }
		        // Otherwise, if in deselected array.
		        else {
		            // Remove from de-selected array.
		            if(($k = array_search($_GET['uri'], $_SESSION['uri_selected'])) !== false) {
		                unset($_SESSION['uri_selected'][$k]);
		            }
		        }
		    }
		}
		elseif($_GET['action'] == 'get_segments') {
		    // Get segment JSON.
		    $data = $api->get_segments($_GET['s'], $_GET['e'], $_GET['history']);
		    // If JSON passed.
		    if(!empty($data)) {
		        // Get UNIX timestamp.
		        $unix_ts = time();
		        // Set in-file filename.
		        $in_file = $unix_ts.'.json';
		        // Make JSON file.
		        if($file->make_json_file($in_file, $data)) {
		            // Set out-file filename.
		            $out_file = $unix_ts.'.'.$_GET['format'];
		            // Make non-JSON file.
		            $file->make_non_json_file($in_file, $out_file, $data, $_GET['format']);
		            // Set file to open automatically, replacing underscre with point, so as to enable JSON data to to be formatted in browser.
		            $this->document = $variable->download_dir.$unix_ts.'.'.str_replace('_', '.', $_GET['format']);
		        }
		    }
		    
		}
		    
		// Output response.
		echo $this->document;
	}
}

?>