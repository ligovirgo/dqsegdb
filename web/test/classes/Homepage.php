<?php
/*
This file is part of the DQSEGDB WUI.

This file was written by Gary Hemming <gary.hemming@ego-gw.it>.

DQSEGDB WUI uses the following open source software:
- jQuery JavaScript Library v1.12.4, available under the MIT licence - http://jquery.org/license - Copyright jQuery Foundation and other contributors.
- W3.CSS 2.79 by Jan Egil and Borge Refsnes.
- Font Awesome by Dave Gandy - http://fontawesome.io.
- Jquery Timepicker, developed and maintained by Willington Vega. Code licensed under the MIT and GPL licenses - http://timepicker.co
*/

// Get libraries.
require_once 'APIRequests.php';
require_once 'Constants.php';
require_once 'DAO.php';

/* Handle homepage. */
class Homepage {
	
	public $home;
	public $homepage_contents;
	public $get_segments_form;
	public $choose_flag_option;
	public $version_div;
	public $version_span;
	
	/* build the homepage. */
	public function build_homepage() {
		// Init.
		$this->home = NULL;
		// Output the homepage container.
		$this->home .= "	<div id=\"div_homepage\" class=\"w3-container w3-padding-0 homepage\">\n";
		// Build.
		$this->home .= "<div class=\"w3-container\">\n";
		// Output the different plots.
		$this->home .= "	<section class=\"w3-container w3-padding-0 w3-responsive\" style=\"overflow-x:scroll\">\n";
		// Build the homepage contents.
		$this->build_homepage_contents();
		$this->home .= $this->homepage_contents;
		// Close section.
		$this->home .= "	</section>\n";
		// Close overall div.
		$this->home .= "</div>\n";
		// Close the homepage container.
		$this->home .= "	</div>\n";
	}

	/* Build the homepage contents. */
	public function build_homepage_contents() {
		// Init.
		$this->homepage_contents = NULL;
		// If on the homepage.
		if($_GET['c'] == 1) {
		    $this->homepage_contents .= "<h3 class=\"w3-text-signal-green\">Get segments</h3>\n";
		    $this->homepage_contents .= "<p id=\"p_get_segments\"><i class=\"fas fa-spinner w3-spin\"></i> Checking connection to server...</p>\n";
		    $this->homepage_contents .= "<div id=\"div_get_segments\" class=\"w3-margin-right\"></div>\n";
		}
	}
	
	/* Build the Get-Segments form as it appears on the homepage. */
	public function build_get_segments_form() {
	    // Init.
	    $this->get_segments_form = NULL;
	    // Instantiate.
	    $api = new APIRequests();
	    $constants = new Constants();
	    $dao = new DAO();
	    // General constants.
	    $constants->general_constants();
	    // Open the form.
	    $this->get_segments_form .= "<form id=\"frm_get_segments\" name=\"frm_get_segments\">\n";
	    $this->get_segments_form .= "<div class=\"w3-container w3-padding w3-dark-grey\">\n";
	    $this->get_segments_form .= "<p><i class=\"fas fa-info-circle\"></i> Use this form to query the server and retrieve segments.</p>\n";
	    $this->get_segments_form .= "</div>\n";
	    // IFO.
	    $this->get_segments_form .= "<div class=\"w3-container w3-border-top\">\n";
	    $this->get_segments_form .= "  <div class=\"w3-container w3-quarter w3-padding-0 w3-padding-top w3-padding-bottom w3-padding-right\">IFO <i class=\"far fa-question-circle cursor\" onclick=\"open_info_modal('ifo')\"></i></div>\n";
	    $this->get_segments_form .= "  <div class=\"w3-container w3-threequarter w3-padding-0\">\n";
	    $this->get_segments_form .= "      <select id=\"ifo\" class=\"w3-input w3-margin-0\" onchange=\"update_flags()\">\n";
	    // Get IFO.
	    $ai = $api->get_ifo_array();
	    // If IFO array has been returned.
	    if(is_array($ai)) {
	        // Init counter.
	        $n = 0;
	        // Add 'All IFO' option.
	        array_unshift($ai['Ifos'], 'Use_all_IFO');
	        // Loop IFO.
    	    foreach($ai['Ifos'] as $k => $ifo) {
    	        $n++;
    	        // If on first loop and no default has yet been set.
    	        if($n == 1 && !isset($_SESSION['ifo'])) {
    	            // Set default host.
    	            $_SESSION['ifo'] = $ifo;
    	        }
    	        // Set selected.
    	        $sel = NULL;
    	        if($ifo == $_SESSION['ifo']) {
    	            $sel = " selected=\"selected\"";
    	        }
    	        $this->get_segments_form .= "          <option value=\"".$ifo."\"".$sel.">".str_replace('_', ' ', $ifo)."</option>\n";
    	    }
	    }
	    $this->get_segments_form .= "      </select>\n";
	    $this->get_segments_form .= "  </div>\n";
	    $this->get_segments_form .= "</div>\n";
	    // Flags.
	    $this->get_segments_form .= "<div class=\"w3-container w3-padding w3-border-top\">\n";
	    $this->get_segments_form .= "  <div class=\"w3-container w3-quarter w3-padding-0 w3-padding-top w3-padding-bottom w3-padding-right\">Flags <i class=\"far fa-question-circle cursor\" onclick=\"open_info_modal('flags')\"></i><br>";
	    $this->get_segments_form .= "  <a onclick=\"switch_choose_flag_option()\" class=\"link\">Switch flag-select view</a>\n";
	    $this->get_segments_form .= "  </div>\n";
	    $this->get_segments_form .= "  <div id=\"div_choose_flag_option\" class=\"w3-container w3-threequarter w3-padding-0\">\n";
	    $this->build_choose_flag_option();
	    $this->get_segments_form .= $this->choose_flag_option;
	    $this->get_segments_form .= "  </div>\n";
	    $this->get_segments_form .= "</div>\n";
	    // Versions.
	    $version_hide = NULL;
	    if(empty($_SESSION['dq_flag'])) {
	        $version_hide = " w3-hide";
	    }
	    $this->get_segments_form .= "<div id=\"div_versions\" class=\"w3-container w3-padding w3-border-top".$version_hide."\">\n";
	    $this->get_segments_form .= "  <div class=\"w3-container w3-quarter w3-padding-0 w3-padding-top w3-padding-bottom w3-padding-right\">Versions <i class=\"far fa-question-circle cursor\" onclick=\"open_info_modal('flag_versions')\"></i></div>\n";
	    $this->get_segments_form .= "  <div id=\"div_versions_field\" class=\"w3-container w3-threequarter w3-padding-0\">\n";
	    $this->get_versions();
	    $this->get_segments_form .= $this->version_div;
	    $this->get_segments_form .= "  </div>\n";
	    $this->get_segments_form .= "</div>\n";
	    // GPS times.
	    $this->get_segments_form .= "<div class=\"w3-container w3-padding w3-border-top\">\n";
	    $this->get_segments_form .= "  <div class=\"w3-container w3-quarter w3-padding-0 w3-padding-top w3-padding-bottom w3-padding-right\">GPS times <i class=\"far fa-question-circle cursor\" onclick=\"open_info_modal('gps_times')\"></i></div>\n";
	    $this->get_segments_form .= "  <div class=\"w3-container w3-threequarter w3-padding-0\">\n";
	    $this->get_segments_form .= "      <input class=\"w3-input w3-half w3-margin-0\" id=\"gps_start_time\" name=\"gps_start_time\" value=\"".$_SESSION['gps_start']."\" min=\"0\" type=\"number\" placeholder=\"GPS start\" />\n";
	    $this->get_segments_form .= "<input class=\"w3-input w3-half w3-margin-0\" id=\"gps_start_time\" name=\"gps_start_time\" value=\"".$_SESSION['gps_stop']."\" min=\"0\" type=\"number\" placeholder=\"GPS stop\" />\n";
	    $this->get_segments_form .= "  </div>\n";
	    $this->get_segments_form .= "</div>\n";
	    // Include history.
	    $this->get_segments_form .= "<div class=\"w3-container w3-padding w3-border-top\">\n";
	    $this->get_segments_form .= "  <div class=\"w3-container w3-quarter w3-padding-0 w3-padding-top w3-padding-bottom w3-padding-right\">Include history? <i class=\"far fa-question-circle cursor\" onclick=\"open_info_modal('include_history')\"></i></div>\n";
	    $this->get_segments_form .= "  <div class=\"w3-container w3-threequarter w3-padding\">\n";
	    foreach($constants->off_on_array as $k => $v) {
	        $check = NULL;
	        if($k == $_SESSION['include_history']) {
	            $check = " checked";
	        }
	        $this->get_segments_form .= "<div class=\"w3-tag w3-light-grey w3-round w3-border w3-margin-right\"><input type=\"radio\" name=\"include_history\" id=\"include_history\" onclick=\"set_include_history(".$k.")\" value=\"".$k."\"".$check."> ".$v."</div>";
	    }
	    $this->get_segments_form .= "  </div>\n";
	    $this->get_segments_form .= "</div>\n";
	    // Output formats.
	    $this->get_segments_form .= "<div class=\"w3-container w3-padding w3-border-top\">\n";
	    $this->get_segments_form .= "  <div class=\"w3-container w3-quarter w3-padding-0 w3-padding-top w3-padding-bottom w3-padding-right\">Output format <i class=\"far fa-question-circle cursor\" onclick=\"open_info_modal('output_formats')\"></i></div>\n";
	    $this->get_segments_form .= "  <div class=\"w3-container w3-threequarter w3-padding\">\n";
	    foreach($dao->get_output_formats() as $k => $of) {
	        $check = NULL;
	        if($of['output_format_id'] == $_SESSION['output_format']) {
	            $check = " checked";
	        }
	        $this->get_segments_form .= "<div class=\"w3-tag w3-light-grey w3-round w3-border w3-margin-right\"><input type=\"radio\" name=\"output_format\" id=\"output_format\" onclick=\"set_output_format(".$of['output_format_id'].")\" value=\"".$of['output_format']."\"".$check."> ".strtoupper(str_replace('_', ' ', $of['output_format']))."</div>";
	    }
	    $this->get_segments_form .= "  </div>\n";
	    $this->get_segments_form .= "</div>\n";
	    // Get-Segments button.
	    $this->get_segments_form .= "<div id=\"div_get_segments_button\" class=\"w3-container w3-padding w3-border-top w3-hide\">\n";
	    $this->get_segments_form .= "  <div class=\"w3-button w3-blue w3-hover-grey w3-center\" onclick=\"get_segments()\"><i class=\"fas fa-save cursor\"></i> Get segments</div>\n";
	    $this->get_segments_form .= "  <span id=\"p_getting_segments\" class=\"w3-hide\"><i class=\"fas fa-spinner w3-spin\"></i> Getting segments...</span>\n";
	    $this->get_segments_form .= "</div>\n";
	    // Close form.
	    $this->get_segments_form .= "</form>\n";
	}
	
	public function build_choose_flag_option() {
	    // Init.
	    $this->choose_flag_option = NULL;
	    // Instantiate.
	    $api = new APIRequests();
	    $constants = new Constants();
	    // General constants.
	    $constants->general_constants();
	    // If using select.
	    if($_SESSION['choose_flag_option'] == 0) {
	        // Open select.
	        $this->choose_flag_option .= "	<select multiple size=\"8\" id=\"dq_flag\" onchange=\"update_flag_versions(".$constants->max_selectable_flags.")\">\n";
	        // If selecting all flags.
	        if($_SESSION['ifo'] == 'Use_all_IFO') {
	            $a = $api->get_all_flags();
	        }
	        // Otherwise, get flags related only to a specific IFO. 
	        else {
	            $a = $api->get_ifo_flags();
	        }
	        // If array has been returned.
	        if(isset($a['results']) && is_array($a['results'])) {
	            // Loop URI array.
	            foreach($a['results'] as $k => $uri) {
	                // If selecting all flags.
	                if($_SESSION['ifo'] == 'Use_all_IFO') {
	                    // Explode to array.
	                    $u = explode('/',$uri);
	                    // If actually at the Use_all_Flags key.
	                    if($u[2] == 'IFO') {
	                        $flag_uri_txt = str_replace('_',' ',$u[3]);
	                        $flag_uri_txt = str_replace('IFO/',' ',$flag_uri_txt);
	                    }
	                    if($u[2] != 'IFO') {
	                        $flag_uri_txt = $u[2].' - '.$u[3];
	                    }
	                }
	                // Or, if selecting flags associated to a specific IFO.
	                else {
	                    // Set simply to flag name.
	                    $flag_uri_txt = $uri;
	                    // Reset URI.
	                    $uri = '/dq/'.$_SESSION['ifo'].'/'.$uri;
	                }
	                // If the DQ Flag session exists, set selected.
	                $sel = NULL;
	                if(isset($_SESSION['dq_flag'])) {
	                    // Explode flags.
	                    $fa = explode(',',$_SESSION['dq_flag']);
	                    // If URI is in array.
	                    if(in_array($uri, $fa)) {
	                        $sel = " selected=\"selected\"";
	                    }
	                }
	                // Set.
	                $this->choose_flag_option .= "		<option value=\"".$uri."\"".$sel.">".$flag_uri_txt."</option>\n";
	            }
	        }
	        // Close select.
	        $this->choose_flag_option .= "	</select>\n";
	    }
	    // Otherwise, if textarea.
	    elseif($_SESSION['choose_flag_option'] == 1) {
	        // Get textarea.
	        $this->choose_flag_option = "	<textarea id=\"ta_dq_flag\" onchange=\"update_flag_versions_from_ta(".$constants->max_selectable_flags.")\"></textarea>\n";
	    }
	}
	
	/* Get the contents of the div containing flag versions. */
	public function get_versions() {
	    // Init.
	    $this->version_div = NULL;
	    // If the DQ Flag session is not empty.
	    if(!empty($_SESSION['dq_flag'])) {
	        // Instantiate.
	        $constant = new Constants();
	        // General constants.
	        $constant->general_constants();
	        // Explode flags.
	        $da = explode(',',$_SESSION['dq_flag']);
	        // If number of selected flags within maximum allowable value.
	        if(count($da) <= $constant->max_selectable_flags) {
	            // Open table.
	            $this->version_div .= "<table class=\"w3-table-all w3-margin-0\">\n";
	            // Loop through selected URI.
	            foreach($da as $k => $uri) {
	                // Explode to get flag.
	                $fa = explode('/', $uri);
	                $u = $fa[2];
	                // If the flag name exists.
	                if(isset($fa[3]) && !empty($fa[3])) {
	                    $flag_name = $fa[3];
	                    $span_name = str_replace('-','_',str_replace(' ','',$fa[3]));
	                    // If selecting from all flags.
	                    if($_SESSION['ifo'] == 'Use_all_IFO') {
	                        $flag_name = $fa[2].' - '.$flag_name;
	                        $span_name = $fa[2].'_'.$span_name;
	                    }
	                    // Get row.
	                    $this->version_div .= "    <tr>\n";
	                    $this->version_div .= "        <td id=\"flag_".$flag_name."\">".$flag_name."</td>\n";
	                    $this->version_div .= "        <td id=\"flag_".$flag_name."_versions\">\n";
	                    // Add version information after flag name.
	                    $this->get_flag_version_span_contents($uri);
	                    $this->version_div .= $this->version_span;
	                    $this->version_div .= "</td>\n";
	                    // Close row.
	                    $this->version_div .= "    </tr>\n";
	                }
	            }
	            // Close table.
	            $this->version_div .= "</table>\n";
	            // Ensure that only flags that have been selected by the user are in the call to the server.
	            foreach($_SESSION['uri_selected'] as $i => $uri) {
	                // Explode to get flag.
	                $fa = explode('/', $uri);
	                $u = $fa[2];
	                $fn = $fa[3];
	                // If flag not found in call to server array.
	                if(!preg_match("/".$u."\/".$fn."/i", $_SESSION['dq_flag'])) {
	                    // Remove from array.
	                    unset($_SESSION['uri_selected'][$i]);
	                }
	            }
	        }
	    }
	}

	/* Get the contents of the flag version span. */
	public function get_flag_version_span_contents($uri) {
	    // Reset the version_span variable.
	    $this->version_span = NULL;
	    // Instantiate.
	    $api = new APIRequests();
        // Explode the URI.
        $e = explode('/', $uri);
        // If flag passed.
        if($e[3]) {
            // If it already contains a version number, N.B. this occurs when 'Use all IFO' is selected.
            if(is_numeric(end($e))) {
                // Remove the last element, i.e. the version number.
                array_pop($e);
                // Re-assemble the URI.
                $uri = implode('/', $e);
            }
            $a = $api->get_uri($uri);
            // If array set.
            if(isset($a['version']) && is_array($a['version'])) {
                // Loop through versions.
                foreach($a['version'] as $k => $v) {
                    // Set URI with version.
                    $uri_v = $uri.'/'.$v;
                    // Set span name.
                    $span_name = 'span_'.$e[2].'_'.$e[3].'_'.$v;
                    // Set class.
                    $check = NULL;
                    if(in_array($uri_v, $_SESSION['uri_selected'])) {
                        $check = ' checked';
                    }
                    // Output versions.
                    $this->version_span .= "<div id=\"".$span_name."\" class=\"w3-tag w3-light-grey w3-round w3-border w3-margin-right\"><input type=\"radio\" name=\"checkbox_".$span_name."\" id=\"checkbox_".$span_name."\" onchange=\"select_version_uri('".$span_name."','".$uri_v."')\" value=\"".$uri_v."\"".$check."> ".$v."</div>";
                }
	        }
	    }
	}

}

?>