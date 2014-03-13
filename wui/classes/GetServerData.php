<?php

// Get libraries.
require_once('DAO.php');
require_once('GetStructure.php');
require_once('InitVar.php');

// Flag class.
class GetServerData
{
	public $query_form;
	public $server_status;
	public $version_div;
	public $version_span;
	
	// Get current server status.
	public function get_current_server_status($content_id) {
		// Instantiate.
		$dao = new DAO();
		// If in right area.
		if($content_id == 27) {
			// Set start time.
			$start_time = microtime();
			// Get host array.
			$host_array = $dao->get_value_array(2);
			// Loop host array.
			foreach($host_array as $key=> $host) {
				// Get file contents.
				$a = json_decode(file_get_contents($host.'/dq'), true);
				// Set stop time.
				$stop_time = microtime();
				// Set elapsed time.
				$elapsed_time = round($stop_time-$start_time, 5);
				// If returned contents are array.
				if(is_array($a)) {
					// Include with p tag.
					$this->server_status = '<p><img src="images/green_arrow.png" alt="" title="" id="green_arrow_virgo" class="green_arrow" />'.$host.' - Virgo instance responding in '.$elapsed_time.' seconds</p>';
				}
				// Otherwise.
				else {
					// Include with p tag.
					$this->server_status = '<p><img src="images/green_faded_arrow.png" alt="" title="" id="green_arrow_virgo" class="green_arrow" />'.$host.' - Virgo instance currently unavailable</p>';
				}
			}
		}
	}

	// Get query form div.
	public function get_query_form_div($tabs) {
		// Init.
		$r = NULL;
		// Instantiate.
		$structure = new GetStructure();
		// Open DIV.
		$structure->openDiv('query_server', $tabs,'');
		$r .= $structure->div;
		// Get query form.
		$this->get_query_form($tabs);
		$r .= $this->query_form;
		// Close DIV.
		$structure->closeDiv('query_server', $tabs);
		$r .= $structure->div;
		// Return.
		return $r;
	}

	// Get query form.
	public function get_query_form($tabs) {
		// Instantiate.
		$dao = new DAO();
		$structure = new GetStructure();
		// OPEN FORM.
		$this->query_form .= "	<form method=\"POST\" id=\"frm_query_server\">\n";
		// GET IFO.
		$f = "IFO";
		$s = "	<select id=\"ifo\" onchange=\"update_div_query_server()\">\n";
		// If the default host has not been set, e.g. from a Jquery request.
		if(!isset($_SESSION['default_host'])) {
			// Set default host.
			$_SESSION['default_host'] = $this->get_quickest_host();
		}
		// Get IFO array.
		$a = json_decode(file_get_contents($_SESSION['default_host'].'/dq'), true);
		// If IFO array has been returned.
		if(is_array($a)) {
			// Init counter.
			$n = 0;
			// Add all IFO.
			array_unshift($a['Ifos'], 'Use_all_IFO');
			// Loop host array.
			foreach($a['Ifos'] as $key => $ifo) {
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
				// Set.
				$s .= "		<option value=\"$ifo\"".$sel.">".str_replace('_', ' ', $ifo)."</option>\n";
			}
		}
		// Close select.
		$s .= "	</select>\n";
		// Add to form.
		$this->query_form .= $structure->get_form_structure($f, $s);
		// GET FLAGS.
		$f = "DQ Flags";
		$s = "	<select multiple size=\"8\" id=\"dq_flag\" onchange=\"update_div_flag_versions()\">\n";
		// If selecting all flags.
		if($_SESSION['ifo'] == 'Use_all_IFO') {
			$res_uri = $_SESSION['default_host'].'/report/flags';
		}
		else {
			$res_uri = $_SESSION['default_host'].'/dq/'.$_SESSION['ifo'];
		}
		// Get URI array.
		$a = json_decode(file_get_contents($res_uri), true);
		// If URI array has been returned.
		if(isset($a['results']) && is_array($a['results'])) {
			// Loop URI array.
			foreach($a['results'] as $key => $uri) {
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
				$s .= "		<option value=\"$uri\"$sel>".$flag_uri_txt."</option>\n";
			}
		}
		// Close select.
		$s .= "	</select>\n";
		// Add flags to form.
		$this->query_form .= $structure->get_form_structure($f, $s);
		// Open div.
		$structure->openDiv('version_div', $tabs,'');
		$this->query_form .= $structure->div;		
		// Add version information.
		$this->get_version_div_contents($tabs);
		$this->query_form .= $this->version_div;
		// Close div.
		$structure->closeDiv('version_div', $tabs);
		$this->query_form .= $structure->div;
		// Add remaining fields, starting with GPS.
		$gps_inputs = "Start: <input id=\"\" class=\"inp_med\" /> End: <input id=\"\" class=\"inp_med\" />";
		$this->query_form .= $structure->get_form_structure('GPS Times', $gps_inputs);
		// Close form.
		$this->query_form .= "	</form>\n";
	}

	// Get the contents of the div containing flag versions.
	public function get_version_div_contents($tabs) {
		// Instantiate.
		$structure = new GetStructure();
		// If the DQ Flag session exists.
		if(isset($_SESSION['dq_flag'])) {
			// Add version information.
			$f = "Versions";
			$s = NULL;
			$i = 0;
			// Explode flags.
			$da = explode(',',$_SESSION['dq_flag']);
			// Loop through selected URI.
			foreach($da as $key => $uri) {
				$i++;
				// Explode to get flag.
				$fa = explode('/', $uri);
				$u = $fa[2];
				$flag_name = $fa[3];
				$span_name = str_replace('-','_',str_replace(' ','',$fa[3]));
				// Get div.
				$cover_div = NULL;
				// Set div colour.
				if($i == 2) {
					$cover_div = "_shaded";
					$i = 0;
				}
				$structure->openDiv('flag_'.$flag_name, $tabs,'div_f_v_cover'.$cover_div);
				$s .= $structure->div;
				// If selecting from all flags.
				if($_SESSION['ifo'] == 'Use_all_IFO') {
					$flag_name = $fa[2].' - '.$flag_name;
					$span_name = $fa[2].'_'.$span_name;
				}
				$s .= $flag_name;
				// Add version information after flag name.
				$this->get_flag_version_span_contents($uri);
				$s .= "<span id=\"span_".$span_name."\" class=\"span_versions\">".$this->version_span."</span>";
				// Close div.
				$structure->closeDiv('flag_'.$flag_name, $tabs);
				$s .= $structure->div;
			}
			// Add to div.
			$this->version_div = $structure->get_form_structure($f, $s);
		}
	}
	
	// Get flag version span.
	public function get_flag_version_span_contents($uri) {
		// Reset the version_span variable.
		$this->version_span = NULL;
		// If related session not set.
		if(!isset($_SESSION['uri_deselected'])) {
			// Set session.
			$_SESSION['uri_deselected'] = array();
		}
		// If args passed.
		if(isset($uri)) {
			// Explode the URI.
			$e = explode('/', $uri);
			// If it already contains a version number, N.B. this occurs when 'Use all IFO' is selected.
			if(is_numeric(end($e))) {
				// Remove the last element, i.e. the version number.
				array_pop($e);
				// Re-assemble the URI.
				$uri = implode('/', $e);
			}
			// Set URI for GET versions call.
			$res_uri = $_SESSION['default_host'].$uri;
			// Get version array.
			$a = json_decode(file_get_contents($res_uri), true);
			// Loop through versions.
			foreach($a['version'] as $key => $v) {
				// Set URI with version.
				$uri_v = $uri.'/'.$v;
				// Set span name.
				$span_name = 'span_'.$e[2].'_'.$e[3].'_'.$v;
				// Set class.
				$class = NULL;
				if(in_array($uri_v, $_SESSION['uri_deselected'])) {
					$class = '_deselected';
				}
				// Output versions.
				$this->version_span .= "<span id=\"".$span_name."\" class=\"span_version_no".$class."\" onclick=\"deselect_version_uri('".$span_name."','".$uri_v."')\">".$v."</span>\n";
			}
		}
	}	
	
	// Get the quickest-replying server host.
	public function get_quickest_host() {
		// Init
		$r = NULL;
		$quickest_reply = 10;
		$elapsed_time = 10;
		// Instantiate.
		$dao = new DAO();
		// Set start time.
		$start_time = microtime();
		// Get host array.
		$host_array = $dao->get_value_array(2);
		// Loop host array.
		foreach($host_array as $key=> $host) {
			// Get file contents.
			$a = json_decode(file_get_contents($host.'/dq'), true);
			// If an array is returned.
			if(is_array($a)) {
				// Set stop time.
				$stop_time = microtime();
				// Set elapsed time.
				$elapsed_time = round($stop_time-$start_time, 5);
			}
			// Check.
			if($elapsed_time < $quickest_reply) {
				// Set as quickest replying host.
				$r = $host;
			}
		}
		// Return.
		return $r;
	}
}

?>