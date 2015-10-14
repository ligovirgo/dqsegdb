<?php

// Get libraries.
require_once('DAO.php');
require_once('GetServerData.php');
require_once('GetStructure.php');

// Page content class.
class GetContent {
	public $contents;
	
	private $page;

	// Get content.
	public function buildContent($tabs) {
		// Initiate.
		$dao = new DAO();
		$structure = new GetStructure();
		$variable = new Variables();
		// Init.
		$variable->getContentCallID();
		$c = $variable->c;
		$this->contents = NULL;
		// Init sessions.
		$variable->initialise_sessions();
 	 	// Check that content actually exists in the database.
 	 	if($dao->checkContentExists($c)) {
			// Get contents.
			if($c == 1) {
				// Get homepage.
				$this->getHomepage($tabs);
			}
			else {
				// Get sub-page.
				$this->getSubpage($c,$tabs);
			}
			// Set.
			$this->contents .= $this->page;
		}
	}

	// Get homepage.
	function getHomepage($tabs) {
		// Instantiate.
		$dao = new DAO();
		$serverdata = new GetServerData();
		$structure = new GetStructure();
		// Init.
		$this->page = NULL;
		$i = 0;
		// Add number of tabs required.
	 	$structure->getRequiredTabs($tabs);
		// Open middle div.
		$structure->openDiv('middle',$tabs,'');
		$this->page .= $structure->div;
		// Open middle_left div.
		$structure->openDiv('middle_left',$tabs+1,'');
		$this->page .= $structure->div;
		// Get left of homepage contents.
		$dao->getHomepageXSQL('l');
		$res = $dao->res;
		// Bind by column name.
		$res->bindColumn('content_id', $content_id);
		$res->bindColumn('content_name', $content_name);
		$res->bindColumn('content_details', $content_details);
		// Loop.
		while($res->fetch()) {
			// Set.
			$i++;
			$content_name = strtoupper($content_name);
			// If outputting query form.
			if($content_id == 24) {
				$content_details .= $serverdata->get_query_form_div($tabs+2);
			}
			// Current status.
			elseif($content_id == 30) {
				$serverdata->get_current_server_status($content_id);
				$content_details .= $serverdata->server_status;
			}
			// Recent query results.
			elseif($content_id == 27) {
				$content_details .= $this->get_recent_query_result_div($tabs+2);
			}
			if($i == 2)
			{
				// Get enclosed display div.
				$structure->getFlatLightBlueDiv('lx_'.$content_id,$content_name,$content_details,NULL,"_on_white",$tabs+2);
				$this->page .= $structure->div;
				$i = 0;
			}
			else {
				// Get enclosed display div.
				$structure->getAzzureDiv('lx_'.$content_id,$content_name,$content_details,NULL,$tabs+2);
				$this->page .= $structure->div;
			}
		}
		// Close middle_left div.
		$structure->closeDiv('middle_left',$tabs+1);
		$this->page .= $structure->div;
		// Open middle_right div.
		$structure->openDiv('middle_right',$tabs+1,'');
		$this->page .= $structure->div;
		// Get right of homepage contents.
		$dao->getHomepageXSQL('r');
		$res = $dao->res;
		$rxStr = NULL;
		// Bind by column name.
		$res->bindColumn('content_id', $content_id);
		$res->bindColumn('content_name', $content_name);
		$res->bindColumn('content_details', $content_details);
		// Loop.
		while($res->fetch()) {
			// Add current server statistics.
			$content_details .= $structure->tabStr."<p><a href=\"?c=34\">Latest Flag/Version/Segment info</a></p>\n";
			$content_details .= $serverdata->get_server_statistics($content_id, $_SESSION['default_host'], NULL, $tabs+2);
			// Add latest Component-Interface and Data-Integrity tests.
			$content_details .= $structure->tabStr."<p><a href=\"?c=40\">Recent Interface/Integrity Tests</a></p>\n";
			$content_details .= $dao->get_last_five_test_runs_for_homepage($tabs+2);
			// Get enclosed display div.
			$structure->getFlatLightBlueDiv('lx_'.$content_id,$content_name,$content_details,NULL,NULL,$tabs+3);
			$rxStr .= $structure->div;
		}
		// Open Dataset Info div.
		$structure->getGreyDiv("dataset_info","Dataset Info",$rxStr,NULL,$tabs+2);
		$this->page .= $structure->div;
		// Close middle-right div.
		$structure->closeDiv('middle_right',$tabs);
		$this->page .= $structure->div;
		// Close middle div.
		$structure->closeDiv('middle',$tabs);
		$this->page .= $structure->div;
	}

	// Get sub-page.
	function getSubpage($c,$tabs) {
		// Instantiate.
		$dao = new DAO();
		$structure = new GetStructure();
		// Init.
		$this->page = NULL;
		// Add number of tabs required.
	 	$structure->getRequiredTabs($tabs);
		// Open middle div.
		$structure->openDiv('middle',$tabs,'');
		$this->page .= $structure->div;
		// Get content.
		$dao->getContentDetails($c);
		$res = $dao->res;
		// Bind by column name.
		$res->bindColumn('content_id', $content_id);
		$res->bindColumn('content_name', $content_name);
		$res->bindColumn('content_details', $content_details);
		// Loop.
		while($res->fetch()) {
			// Add authentication form.
			$content_details .= $this->get_authentication_form($content_id, $tabs);
			// Add server log files.
			$content_details .= $this->get_server_log_files($content_id, $tabs);
			// Add server statistics for all available IFO on all available hosts.
			$content_details .= $this->get_all_server_statistics($content_id, $tabs+2);
			// Add flag statistics for the currently-selected host.
			$content_details .= $this->get_flag_statistics($content_id, $tabs+2);
			// Add process information for the currently-selected host.
			$content_details .= $this->get_processes($content_id, $tabs+2);
			// Get JSON Payloads.
			$content_details .= $this->get_payloads($content_id, $tabs+2);
			// Get Regression Tests.
			$content_details .= $this->get_regression_tests($content_id, $tabs+2);
			// Get enclosed display div.
			$structure->getFlatLightBlueDiv('div_content_'.$content_id,$content_name,$content_details,NULL,"_on_white",$tabs+1);
		}
		$this->page .= $structure->div;
		// Close middle div.
		$structure->closeDiv('middle',$tabs);
		$this->page .= $structure->div;
	}

	// Get authentication form.
	private function get_authentication_form($c, $tabs) {
		// Init.
		$r = NULL;
		// If in the correct area.
		if($c == 18) {
			// Init.
			$str = NULL;
			// Instantiate.
			$structure = new structure();
			$user = new user();
			// Add number of tabs required.
		 	$tab_str = $structure->getRequiredTabs($tabs);
			// If not yet logged-in.
			if(1) {
				// Open form.
				$r .= $tab_str."<form id=\"frm_aut\" name=\"frm_aut\" method=\"post\" >\n";
				// Get username row.
				$r .= $structure->getFormElement("user","Username","username","text",NULL,"inp_med",NULL,NULL,NULL,NULL,FALSE,$tabs+1);
				// Get Password row.
				$r .= $structure->getFormElement("pass","Password","password","password",NULL,"inp_med",NULL,NULL,NULL,NULL,FALSE,$tabs+1);
				// Get button row.
				$r .= $structure->getFormElement("submit",NULL,"submit","image",NULL,"no_border","onclick=\"redirect('frm_aut','includes/authenticate.php?aut_type=TRUE')\"", NULL, NULL, FALSE, $tabs+1);
				// Close form.
				$r .= $tab_str."</form>\n";
			}
			// Otherwise, if logged-in.
			else {
				$r .= "<p>You are already logged-in to the DQSEGDB WUI Intranet. Click on the icon below to log-out.</p>";
				$r .= "<p><a href=\"includes/authenticate.php\"><img src=\"images/logout.png\" id=\"img_logout\" /></a></p>";
			}
		}
		// Return.
		return $r;
	}

	// Get server log files.
	function get_server_log_files($c,$tabs) {
		// Init.
		$r = NULL;
		// If in the correct area.
		if($c == 29) {
			// Init.
			$r = NULL;
			$i = 0;
			$e = 0;
			$get_f = NULL;
			if(isset($_GET['f'])) {
				$get_f = $_GET['f'];
			}
			$max_files = 14;
			$max_events = 50;
			$events = NULL;
			$called_file_events = NULL;
			$log_files = NULL;
			// Instantiate.
			$structure = new GetStructure();
			// Add number of tabs required.
		 	$structure->getRequiredTabs($tabs);
			// Set log file dir.
			$dir = "/opt/dqsegdb/python_server/logs/";
			$files = glob("$dir*");
			rsort($files);
			// Build array.
			foreach($files as $file) {
				// Increment counter.
				$i++;
				// If within max number of files for display.
				if($i <= $max_files) {
					// Get filename reversed string.
					$a = explode('/', strrev($file));
					$f = strrev($a[0]);
					// Get filesize.
					$fs = round(filesize($file)/1000);
					// If not called file.
					if($f != $get_f) {
						$log_files .= "<a href=\"?c=".$c."&f=".$f."#f_".$f."\">".$f."</a> (".$fs."Kb)<br />\n";
					}
					else {
						$log_files .= "<a name=\"f_".$f."\"></a><strong>".$f."</strong> (".$fs."Kb)<br />\n";
					}
				}
				// If on first loop or a file is being called.
				if($i == 1 || $f == $get_f) {
					// If on first loop.
					if($i == 1) {
						$r .= "<p><strong>".$max_events." most recently logged events (".$f."):</strong></p>\n";
					}
					// Get individual rows.
					$b = explode("\n", file_get_contents($file));
					// Reverse sort contents.
					rsort($b);
					// Loop contents.
					foreach($b as $fc) {
						// Increment.
						$e++;
						if($i == 1 && $e <= $max_events) {
							$events .= substr($fc, 1)."<br />\n";
						}
						elseif($f == $get_f) {
							$called_file_events .= substr($fc, 1)."<br />\n";
						}
					}
					if($f == $get_f) {
						$log_files .= "<code>".substr($called_file_events, 0, -7)."</code>\n";
					}
					// If on first loop.
					if($i == 1) {
						// Incorporate in p tag.
						$r .= "<code>".substr($events, 0, -7)."</code>\n";
						$r .= "<p><strong>Most recent log files:</strong></p>\n";
						// If not viewing an individual file.
						if(!$get_f) {
							$r .= "<p>Click on a filename to view the contents.</p>\n";
						}
						else {
							$r .= "<p><a href=\"?c=".$c."\">Stop viewing file contents</a></p>\n";
						}
					}
				}
			}
			// Incorporate in code tag.
			$r .= "<code>".substr($log_files, 0, -7)."</code>\n";
		}
		// Return.
		return $r;
	}

	// Get recent query results div.
	public function get_recent_query_result_div($tabs) {
		// Init.
		$r = NULL;
		// Instantiate.
		$dao = new DAO();
		$structure = new GetStructure();
		// Open div.
		$structure->openDiv('payload_filter_form', $tabs,'');
		$r .= $structure->div;
		// Get results.
		$r .= $dao->get_recent_query_results(5, TRUE, $tabs+1);
		// Close div.
		$structure->closeDiv('payload_filter_form', $tabs);
		$r .= $structure->div;
		// Return.
		return $r;
	}
	
	// Add flag statistics for the currently-selected host.
	private function get_flag_statistics($c, $tabs) {
		// Init.
		$r = NULL;
		// If in correct section.
		if($c == 35) {
			// Instantiate.
			$dao = new DAO();
			$serverdata = new GetServerData();
			$structure = new GetStructure();
			// Add number of tabs required.
			$structure->getRequiredTabs($tabs);
			// If current host is set.
			if(isset($_SESSION['default_host'])) {
				// Get additional text available for this host.
				$add_info = $dao->get_value_add_info($_SESSION['default_host']);
				// Set host name.
				$host_name = $serverdata->set_host_name($_SESSION['default_host'], $add_info);
				// Output header.
				$r .= $structure->tabStr."<h3>".$host_name." flag statistics</h3>\n";
				// Get array of IFO available on current host.
				$a_i = $serverdata->get_ifo_array($_SESSION['default_host']);
				// If IFO returned.
				if(!empty($a_i)) {
					// Output header.
					$r .= $structure->tabStr."<p>To view flag statistics for a specific IFO on this host, click on the relevant link below:</p>\n";
					// Indent.
					$r .= $structure->tabStr."<ul>\n";
					// Loop IFO.
					foreach($a_i['Ifos'] as $ifo_id => $ifo) {
						// Output link.
						$r .= $structure->tabStr."	<li><a href=\"#".$ifo."\">".$ifo."</a></li>\n";
					}
					// Indent.
					$r .= $structure->tabStr."</ul>\n";
					// Loop IFO.
					foreach($a_i['Ifos'] as $ifo_id => $ifo) {
						// Output header.
						$r .= $structure->tabStr."<h4><a name=\"".$ifo."\"></a>".$ifo."</h4>\n";
						// Get the flag statistics table.
						$r .= $serverdata->get_flag_statistics_table($c, $_SESSION['default_host'], $ifo, $tabs);
					}
				}
			}
		}
		// Return.
		return $r;
	}

	// Get server statistics for all available IFO on all available hosts.
	private function get_all_server_statistics($c, $tabs) {
		// Init.
		$r = NULL;
		// If in correct section.
		if($c == 34) {
			// Instantiate.
			$dao = new DAO();
			$serverdata = new GetServerData();
			$structure = new GetStructure();
			// Add number of tabs required.
		 	$structure->getRequiredTabs($tabs);
			// Get all available hosts.
			$a = $dao->get_value_array(2);
			// Output intro.
			$r .= $structure->tabStr."<p>Click on a link below to go straight to the statistics for a specific host.</p>\n";
			// Indent.
			$r .= $structure->tabStr."<ul>\n";
			// First of all, loop through and output internal links.
			foreach($a as $key => $host) {
				// If currently in use.
				if($dao->get_value_add_int($host)) {
					// Get additional text available for this host.
					$add_info = $dao->get_value_add_info($host);
					// Set host name.
					$host_name = $serverdata->set_host_name($host, $add_info);
					// Set.
					$r .= $structure->tabStr."	<li><a href=\"#".$host."\">".$host_name."</a></li>\n";
				}
			}
			// Stop indent.
			$r .= $structure->tabStr."</ul>\n";
			// Loop through host array.
			foreach($a as $key => $host) {
				// If currently in use.
				if($dao->get_value_add_int($host)) {
					// Get additional text available for this host.
					$add_info = $dao->get_value_add_info($host);
					// Set host name.
					$host_name = $serverdata->set_host_name($host, $add_info);
					// Output header.
					$r .= $structure->tabStr."<h3><a name=\"".$host."\"></a>".$host_name."</h3>\n";
					// Get host statistics.
					$r .= $serverdata->get_server_statistics($c, $host, NULL, $tabs);
					// Get array of IFO available on this host.
					$a_i = $serverdata->get_ifo_array($host);
					// If array has been returned.
					if(isset($a_i['Ifos']) && is_array($a_i['Ifos'])) {
						// Loop through each IFO.
						foreach($a_i['Ifos'] as $key_i => $ifo) {
							// Output header.
							$r .= $structure->tabStr."<h4>".$ifo."</h4>\n";
							// Get IFO statistics.
							$r .= $serverdata->get_server_statistics($c, $host, $ifo, $tabs);
						}
					}
				}
			}
		}
		// Return.
		return $r;
	}
	
	// Add recently-run processes for the currently-selected host.
	private function get_processes($c, $tabs) {
		// Init.
		$r = NULL;
		// If in correct section.
		if($c == 38) {
			// Instantiate.
			$dao = new DAO();
			$serverdata = new GetServerData();
			$structure = new GetStructure();
			// Add number of tabs required.
			$structure->getRequiredTabs($tabs);
			// If current host is set.
			if(isset($_SESSION['default_host'])) {
				// Get additional text available for this host.
				$add_info = $dao->get_value_add_info($_SESSION['default_host']);
				// Set host name.
				$host_name = $serverdata->set_host_name($_SESSION['default_host'], $add_info);
				// Output header.
				$r .= $structure->tabStr."<h3>".$host_name." processes</h3>\n";
				// Get array of IFO available on current host.
				$a_i = $serverdata->get_ifo_array($_SESSION['default_host']);
				// If IFO returned.
				if(!empty($a_i)) {
					// Get the processes table.
					$r .= $serverdata->get_processes_table($c, $_SESSION['default_host'], $tabs);
				}
			}
		}
		// Return.
		return $r;
	}

	// Add payloads produced via the web interface.
	private function get_payloads($c, $tabs) {
		// Init.
		$r = NULL;
		// If in correct section.
		if($c == 39) {
			// Instantiate.
			$dao = new DAO();
			$serverdata = new GetServerData();
			$structure = new GetStructure();
			$variable = new Variables();
			// Add number of tabs required.
			$structure->getRequiredTabs($tabs);
			// Get payload limit.
			$variable->get_app_variables();
			// Open table.
			$r .= $this->get_payload_filter_form($tabs+1);
			// Open payload filter form div.
			$structure->openDiv('payload_filter_form', $tabs,'');
			$r .= $structure->div;
			// Get query results.
			$r .= $dao->get_recent_query_results($variable->payloads_to_display, FALSE, $tabs+1);
			// Close payload filter form div.
			$structure->closeDiv('payload_filter_form',$tabs);
			$r .= $structure->div;
		}
		// Return.
		return $r;
	}
	
	// Get payload filter form.
	public function get_payload_filter_form($tabs) {
		// Init.
		$r = NULL;
		// Instantiate.
		$dao = new DAO();
		$structure = new GetStructure();
		$variable = new Variables();
		// Get app variables.
		$variable->get_app_variables();
		// Get content call ID.
		$variable->getContentCallID();
		// OPEN FORM.
		$r .= "	<form id=\"frm_payload_filter\">\n";
		// USERS.
		$f = 'User';
		$s = "	<select id=\"user_id\" name=\"user_id\" onchange=\"update_payloads(".$variable->c.")\">\n";
		// Set selected.
		$sel = NULL;
		if(isset($_SESSION['filter_user'])) {
			if($_SESSION['filter_user'] == 0) {
				$sel = " selected=\"selected\"";
			}
		}
		// Set blank option.
		$s .= "		<option value=\"0\"".$sel."></option>\n";
		// Get user array.
		$a = $dao->get_value_array(3);
		// If user array has been returned.
		foreach($a as $user_id => $username) {
			// Set selected.
			$sel = NULL;
			if(isset($_SESSION['filter_user'])) {
				if($user_id == $_SESSION['filter_user']) {
					$sel = " selected=\"selected\"";
				}
			}
			// Set options.
			$s .= "		<option value=\"".$user_id."\"".$sel.">".$username."</option>\n";
		}
		// Close select.
		$s .= "	</select>\n";
		// Add to form.
		$r .= $structure->get_form_structure($f, $s, NULL);
		// DATA.
		$f = 'Data';
		$s = "	<select id=\"data_id\" name=\"data_id\" onchange=\"update_payloads(".$variable->c.")\">\n";
		// Set selected.
		$sel = NULL;
		if(isset($_SESSION['filter_data'])) {
			if($_SESSION['filter_data'] == 0) {
				$sel = " selected=\"selected\"";
			}
		}
		// Set blank option.
		$s .= "		<option value=\"0\"".$sel."></option>\n";
		// Get data array.
		$a = $dao->get_value_array(2);
		// If data array has been returned.
		foreach($a as $data_id => $dataset) {
			// Get full host name from ID.
			$host = $dao->get_full_host_name_from_id($data_id);
			// Set selected.
			$sel = NULL;
			if(isset($_SESSION['filter_data'])) {
				if($data_id == $_SESSION['filter_data']) {
					$sel = " selected=\"selected\"";
				}
			}
			// Set options.
			$s .= "		<option value=\"".$data_id."\"".$sel.">".$host."</option>\n";
		}
		// Close select.
		$s .= "	</select>\n";
		// Add to form.
		$r .= $structure->get_form_structure($f, $s, NULL);
		// Close form.
		$r .= "	</form>\n";
		// Return.
		return $r;
	}
	
	// Add regression test runs.
	private function get_regression_tests($c, $tabs) {
		// Init.
		$r = NULL;
		// If in correct section.
		if($c == 40) {
			// Instantiate.
			$dao = new DAO();
			$structure = new GetStructure();
			$variable = new Variables();
			// Add number of tabs required.
			$structure->getRequiredTabs($tabs);
			// If viewing specific RTS run.
			if(isset($_GET['r'])) {
				// Get specific regression test.
				$r .= $dao->specific_regression_test($_GET['r'], $tabs+1);
			}
			// Otherwise, if viewing all RTS runs.
			else {
				// Get rts limit.
				$variable->get_app_variables();
				// Get recent regression tests.
				$r .= $dao->get_recent_regression_test_runs($variable->rts_to_display, FALSE, $tabs+1);
			}
		}
		// Return.
		return $r;
	}
	
}

?>