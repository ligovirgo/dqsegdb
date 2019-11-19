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
require_once 'Logger.php';

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
	    $this->get_segments_form .= "  <div class=\"w3-container w3-threequarter w3-padding\">\n";
	    // Get IFO.
	    $ai = $api->get_ifo_array();
	    // If IFO array has been returned.
	    if(is_array($ai)) {
	        // Loop IFO.
	        foreach($ai['Ifos'] as $k => $ifo) {
	            $ifo_class = 'w3-white';
	            if(!key_exists($ifo, $_SESSION['deselected_ifo'])) {
	                $ifo_class = 'w3-blue';
	            }
	            $this->get_segments_form .= "<div id=\"div_ifo_".$ifo."\" class=\"w3-tag ".$ifo_class." w3-hover-grey w3-border w3-round w3-margin-right cursor\" onclick=\"deselect_ifo('".$ifo."')\">".str_replace('_', ' ', $ifo)."</div>";
	        }
	    }
	    $this->get_segments_form .= "      </select>\n";
	    $this->get_segments_form .= "  </div>\n";
	    $this->get_segments_form .= "</div>\n";
	    // Flags.
	    $this->get_segments_form .= "<div class=\"w3-container w3-padding w3-border-top\">\n";
	    $this->get_segments_form .= "  <div class=\"w3-container w3-quarter w3-padding-0 w3-padding-top w3-padding-bottom w3-padding-right\">Flags <i class=\"far fa-question-circle cursor\" onclick=\"open_info_modal('flags')\"></i><br>";
	    //$this->get_segments_form .= "  <a onclick=\"switch_choose_flag_option()\" class=\"link\">Switch flag-select view</a>\n";
	    $this->get_segments_form .= "  </div>\n";
	    $this->get_segments_form .= "  <div class=\"w3-container w3-threequarter w3-padding-0\">\n";
	    $this->get_segments_form .= "      <div class=\"w3-container w3-padding-0 w3-margin-0\">\n";
	    $this->get_segments_form .= "          <input class=\"w3-input w3-margin-0\" id=\"flag_filter\" name=\"flag_filter\" value=\"".$_SESSION['flag_filter']."\" type=\"text\" placeholder=\"Start typing part of a flag name here to filter...\" onkeypress=\"filter_flag_list()\" />\n";
	    $this->get_segments_form .= "      </div>\n";
	    $this->get_segments_form .= "      <div id=\"div_choose_flag_option\" class=\"w3-container w3-padding-0 w3-margin-0\">\n";
	    $this->build_choose_flag_option_multiple_ifo();
	    $this->get_segments_form .= $this->choose_flag_option;
	    $this->get_segments_form .= "      </div>\n";
	    $this->get_segments_form .= "  </div>\n";
	    $this->get_segments_form .= "</div>\n";
	    // Versions.
	    $version_hide = NULL;
	    if(empty($_SESSION['dq_flag_uris'])) {
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
	    $this->get_segments_form .= "<input class=\"w3-input w3-half w3-margin-0\" id=\"gps_stop_time\" name=\"gps_stop_time\" value=\"".$_SESSION['gps_stop']."\" min=\"0\" type=\"number\" placeholder=\"GPS stop\" />\n";
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
	    $get_segments_button_hide = NULL;
	    if(empty($_SESSION['dq_flag_uris'])) {
	        $get_segments_button_hide = " w3-hide";
	    }
	    $this->get_segments_form .= "<div id=\"div_get_segments_button\" class=\"w3-container w3-padding w3-border-top".$get_segments_button_hide."\">\n";
	    $this->get_segments_form .= "  <div id=\"btn_get_segments\" class=\"w3-button w3-blue w3-hover-grey w3-center\" onclick=\"get_segments()\"><i class=\"fas fa-save cursor\"></i> Get segments</div>\n";
	    $this->get_segments_form .= "  <span id=\"p_getting_segments\" class=\"w3-hide\"><i class=\"fas fa-spinner w3-spin\"></i> Getting segments...</span>\n";
	    $this->get_segments_form .= "</div>\n";
	    // Close form.
	    $this->get_segments_form .= "</form>\n";
	}
	
	/* Build the choose-flag option when using multiple IFO. */
	public function build_choose_flag_option_multiple_ifo() {
	    // Init.
	    $this->choose_flag_option = NULL;
	    $flag_count = 0;
	    $already_output_array = array();
	    // Instantiate.
	    $api = new APIRequests();
	    $constants = new Constants();
	    // General constants.
	    $constants->general_constants();
	    // If using select.
	    if($_SESSION['choose_flag_option'] == 0) {
	        // Open select.
	        $this->choose_flag_option .= "	<ul id=\"div_dq_flags\" class=\"w3-ul w3-border\" style=\"height:200px;overflow-y:scroll\">\n";
	        // Get all flags.
            $a = $api->get_all_flags();
	        // If array has been returned.
	        if(isset($a['results']) && is_array($a['results'])) {
	            // Loop URI array.
	            foreach($a['results'] as $k => $uri) {
                    // Explode to array.
                    $u = explode('/',$uri);
                    $ifo = $u[2];
                    $flag = $u[3];
                    $ifo_flag = $ifo."___".$flag;
                    // If the second key in the array is not deselected.
                    if(!key_exists($ifo, $_SESSION['deselected_ifo'])) {
                        // By default, show the flag.
                        $class = NULL;
                        // If the flag has already been selected.
                        if(key_exists($ifo_flag, $_SESSION['dq_flag_uris'])) {
                            // Hide it.
                            $class = ' w3-hide';
                        }
                        // If the flag filter is not empty or matches with the name of the field.
                        if(empty($_SESSION['flag_filter'])
                        || preg_match('/'.$_SESSION['flag_filter'].'/i', $flag)) {
                            // If the flag has not been output.
                            if(!in_array($ifo_flag, $already_output_array)) {
                                // Set.
                                $this->choose_flag_option .= "		<li id=\"li_".$ifo_flag."\" class=\"w3-border-bottom w3-hover-light-grey cursor".$class."\" onclick=\"select_flag('".$ifo_flag."')\">".str_replace('___', ':', $ifo_flag)."</li>\n";
                	            // Increment the flag counter.
                	            $flag_count++;
                	            // Add to the output array.
                	            array_push($already_output_array, $ifo_flag);
                            }
                        }
                    }
	            }
	        }
	        // Close select.
	        $this->choose_flag_option .= "	</ul>\n";
	        // If no flags available.
	        if($flag_count == 0) {
	            // Re-write the created variable.
	            $this->choose_flag_option = "	<p><i class=\"fas fa-exclamation-circle\"></i> No flags are available for the current selection.</p>\n";
	        }
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
	    // If the DQ Flag URI session is not empty.
	    if(!empty($_SESSION['dq_flag_uris'])) {
	        // Instantiate.
	        $constant = new Constants();
	        // General constants.
	        $constant->general_constants();
	        // If number of selected flags within maximum allowable value.
	        if(count($_SESSION['dq_flag_uris']) <= $constant->max_selectable_flags) {
	            // Open table.
	            $this->version_div .= "<table class=\"w3-table-all w3-margin-0\">\n";
	            // Loop through selected URI.
	            foreach($_SESSION['dq_flag_uris'] as $ifo_flag => $versions) {
                    // Get row.
	                $this->version_div .= "    <tr id=\"tr_".$ifo_flag."\">\n";
	                $this->version_div .= "        <td id=\"flag_".$ifo_flag."\">\n";
	                $this->version_div .= "            <div class=\"w3-tag w3-red w3-hover-light-grey w3-round w3-border w3-margin-right cursor\" onclick=\"deselect_flag('".$ifo_flag."', .".$constant->max_selectable_flags.")\"><i class=\"far fa-times-circle\"></i></div>".str_replace('___', ':', $ifo_flag)."\n";
                    $this->version_div .= "        </td>\n";
                    $this->version_div .= "        <td id=\"flag_".$ifo_flag."_versions\">\n";
                    // Add version information after flag name.
                    $this->get_flag_version_span_contents($ifo_flag, $versions);
                    $this->version_div .= $this->version_span;
                    $this->version_div .= "</td>\n";
                    // Close row.
                    $this->version_div .= "    </tr>\n";
	            }
	            // Close table.
	            $this->version_div .= "</table>\n";
	        }
	    }
	}
	
	/* Check if it a flag-version has already been selected and, if not, add it to the selected array. */
	public function add_version_to_session($u, $flag_name) {
	    // Init.
	    $exists = FALSE;
	    // Loop through the selected flag-versions.
	    foreach($_SESSION['uri_selected'] as $k => $uri) {
	        // If the flag name exists.
	        if(preg_match('/'.$flag_name.'/i', $uri)) {
	            $exists = TRUE;
	            break;
	        }
	    }
	    // If the URI does not exist, add it as a default.
	    if(!$exists) {
	        array_push($_SESSION['uri_selected'], $u);
	    }
	}

	/* Get the contents of the flag version span. */
	public function get_flag_version_span_contents($ifo_flag, $selected_versions) {
	    // Reset the version_span variable.
	    $this->version_span = NULL;
	    // Instantiate.
	    $api = new APIRequests();
	    // Get the JSON payload for this flag.
	    $a = $api->get_uri('/dq/'.str_replace('___', '/', $ifo_flag));
        // If array set.
        if(isset($a['version']) && is_array($a['version'])) {
            // Loop through versions.
            foreach($a['version'] as $k => $v) {
                // Set span name.
                $span_name = 'span_'.$ifo_flag.'_'.$v;
                // Set class.
                $check = NULL;
                if(in_array($v, $selected_versions)) {
                    $check = ' checked';
                }
                // Output versions.
                $this->version_span .= "<div id=\"".$span_name."\" class=\"w3-tag w3-light-grey w3-round w3-border w3-margin-right\"><input type=\"radio\" name=\"checkbox_".$span_name."\" id=\"checkbox_".$span_name."\" onchange=\"select_version_uri('".$ifo_flag."','".$v."')\" value=\"".v."\"".$check."> ".$v."</div>";
            }
	    }
	}

}

?>