//# Copyright (C) 2014-2020 Syracuse University, European Gravitational Observatory, and Christopher Newport University.  Written by Ryan Fisher and Gary Hemming. See the NOTICE file distributed with this work for additional information regarding copyright ownership.

//# This program is free software: you can redistribute it and/or modify

//# it under the terms of the GNU Affero General Public License as

//# published by the Free Software Foundation, either version 3 of the

//# License, or (at your option) any later version.

//#

//# This program is distributed in the hope that it will be useful,

//# but WITHOUT ANY WARRANTY; without even the implied warranty of

//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the

//# GNU Affero General Public License for more details.

//#

//# You should have received a copy of the GNU Affero General Public License

//# along with this program.  If not, see <http://www.gnu.org/licenses/>.
<?php

// Get libraries.
require_once('InitVar.php');
require_once('GetServerData.php');

// Data Access Object class.
class DAO
{
	public $pdo;
	public $res;
	public $resB;

	/////////////////////////
	// GENERAL CONNECTION //
	///////////////////////

	// Connect to database.	
	public function dbConnect() {
		// Create new variables object.
		$variable = new Variables();
		$variable->initVariables();
		// If connection not made.
		if(!$this->pdo) {
			// Create new PDO object.
			$this->pdo = new PDO("mysql:host=".$variable->host.";dbname=".$variable->db, $variable->db_user, $variable->db_pass);
/*			// Check.
			if(!isset($this->pdo))
			{
				echo "Connection failed: ";
				print_r($this->pdo->errorInfo());
				exit();
			}
			else
			{
				echo "Connection made!";
				print_r($this->pdo->errorInfo());
			}
*/		}
	}

	// Connect to RTS database.	
	public function db_rts_connect() {
		// Create new variables object.
		$variable = new Variables();
		$variable->initVariables();
		// If connection not made.
		if(!isset($this->pdo_rts)) {
			// Create new PDO object.
			$this->pdo_rts = new PDO("mysql:host=".$variable->host_rts.";dbname=".$variable->db_rts, $variable->db_user, $variable->db_pass);
		}
	}
	
	///////////////////
	// HOST-RELATED //
	/////////////////
	
	// Get default host.
	public function get_default_host() {
		// Init.
		$r = '';
		// Create PDO object
		$this->dbConnect();
		// Build prepared statement.
		if(($stmt = $this->pdo->prepare("SELECT value_txt
										 FROM tbl_values
										 WHERE value_group_fk=2 AND value_second_add_int=1"))) {
			// Execute.
			if($stmt->execute()) {
				// Bind by column name.
				$stmt->bindColumn('value_txt', $value_txt);
				// Loop.
				while($stmt->fetch()) {
					// Check again.
					$r = $value_txt;
				}
			}
		}
		// Return.
		return $r;
	}
	
	////////////////////////
	// STRUCTURE-RELATED //
	//////////////////////

	// Get contents as top links.
	public function getTopLinkSQL() {
		// Create PDO object
		$this->dbConnect();
		// Query.
		$this->res = $this->pdo->query("SELECT content_id, content_name, content_uri
										FROM tbl_contents
										WHERE content_parent=0 AND content_hide_in_top_links=0");
	}

	// Get sub-link SQL.
	public function getSubLinkSQL($c) {
		// If arg sent.
		if(isset($c))
		{
			// Create PDO object
			$this->dbConnect();
			// Build prepared statement.
			if(($stmt = $this->pdo->prepare("SELECT content_id, content_name, content_uri
							 				 FROM tbl_contents
							 				 WHERE content_parent=:c AND content_hide_in_top_links=0
											 ORDER BY content_name"))) {
				// Execute.
				if($stmt->execute(array(':c' => $c))) {
					// Loop.
					$this->resB = $stmt;
				}
			}
		}
	}

	// Get footer SQL.
	public function getFooterSQL() {
		// Init.
		$ToF = FALSE;
		// Create PDO object
		$this->dbConnect();
		// Query.
		$this->res = $this->pdo->query("SELECT content_id, content_name
						FROM tbl_contents
						WHERE content_inc_in_footer=1");
	}

	// Get homepage left contents.
	public function getHomepageXSQL($lr) {
		// Create PDO object
		$this->dbConnect();
		// Query.
		$this->res = $this->pdo->query("SELECT content_id, content_name, content_details
						FROM tbl_contents
						WHERE content_inc_on_homepage_".$lr."x=1
						ORDER BY content_id");
	}

	// Check if content has sub-links
	public function checkForSubLinks($c) {
		// Init.
		$ToF = FALSE;
		// If arg sent.
		if(isset($c)) {
			// Create PDO object
			$this->dbConnect();
			// Build prepared statement.
			$stmt = $this->pdo->prepare("SELECT content_id
						     FROM tbl_contents
						     WHERE content_parent=:c AND content_parent<>1 AND content_hide_in_top_links=0
						     LIMIT 1");
			// Execute.
			if($stmt->execute(array(':c' => $c))) {
				// Loop.
				while($stmt->fetch()) {
					// Set.
					$ToF = TRUE;
				}
			}
		}
		// Return.
		return $ToF;
	}

	// Check if this is the content section currently being used.
	public function checkIfSectionSel($c,$p) {
	 	// Init.
	 	$sel = FALSE;
		// If args are passed.
		if(isset($c) && isset($p)) {
			// Create PDO object
			$this->dbConnect();
			// If the content is already the parent.
			if($c == $p) {
				// Set.
				$sel = TRUE;
			}
			// Otherwise, if not at root.
			elseif($c != 0 && $c != 99999 && $sel == FALSE) {
				// Build prepared statement.
				if(($stmt = $this->pdo->prepare("SELECT content_parent
								 FROM tbl_contents
								 WHERE content_id=:c
								 LIMIT 1"))) {
					if($stmt->execute(array(':c' => $c))) {
						// Bind by column name.
						$stmt->bindColumn('content_parent', $content_parent);
						// Loop.
//$stmt->fetch(PDO::FETCH_BOUND)
						while($stmt->fetch()) {
							// Check again.
							$sel = $this->checkIfSectionSel($content_parent,$p);
						}
					}
				}
			}
		}
		// Return.
		return $sel;
	}

	//////////////////////
	// CONTENT-RELATED //
	////////////////////

	// Check if content exists
	public function checkContentExists($c) {
		// Init.
		$ToF = FALSE;
		// If arg sent.
		if(isset($c)) {
			// Create PDO object
			$this->dbConnect();
			// Build prepared statement.
			if(($stmt = $this->pdo->prepare("SELECT content_id
							 FROM tbl_contents
							 WHERE content_id=:c
							 LIMIT 1"))) {
				// Execute.
				if($stmt->execute(array(':c' => $c))) {
					// Loop.
					while($stmt->fetch()) {
						// Set.
						$ToF = TRUE;
					}
				}
			}
		}
		// Return.
		return $ToF;
	}

	// Get content details.
	public function getContentDetails($c) {
		// If arg sent.
		if(isset($c) && $this->checkContentExists($c)) {
			// Create PDO object
			$this->dbConnect();
			// Build prepared statement.
			if(($stmt = $this->pdo->prepare("SELECT content_id, content_name, content_details
							 				 FROM tbl_contents
							 				 WHERE content_id=:c"))) {
				// Execute.
				if($stmt->execute(array(':c' => $c))) {
					// Loop.
					$this->res = $stmt;
				}
			}
		}
	}

	// Get content parent.
	public function get_content_parent($c) {
		// Init.
		$r = 0;
		// If arg sent.
		if(isset($c)) {
			// Create PDO object
			$this->dbConnect();
			// Build prepared statement.
			if(($stmt = $this->pdo->prepare("SELECT content_parent
							 				 FROM tbl_contents
							 				 WHERE content_id=:c"))) {
				// Execute.
				if($stmt->execute(array(':c' => $c))) {
					// Bind by column name.
					$stmt->bindColumn('content_parent', $content_parent);
					// Loop.
					while($stmt->fetch()) {
						// Check again.
						$r = $content_parent;
					}
				}
			}
		}
		// Return.
		return $r;
	}

	////////////////////
	// VALUE-RELATED //
	//////////////////

	// Get an array of values.
	public function get_value_array($g) {
		// Init.
		$a = array();
		// If arg sent.
		if(isset($g)) {
			// Create PDO object
			$this->dbConnect();
			// Build prepared statement.
			if(($stmt = $this->pdo->prepare("SELECT value_id, value_txt
							 				 FROM tbl_values
							 				 WHERE value_group_fk=:g"))) {
				// Execute.
				if($stmt->execute(array(':g' => $g))) {
					// Bind by column name.
					$stmt->bindColumn('value_id', $value_id);
					$stmt->bindColumn('value_txt', $value_txt);
					// Loop.
					while($stmt->fetch()) {
						// Check again.
						$a[$value_id] = $value_txt;
					}
				}
			}
		}
		// Return.
		return $a;
	}
	
	// Get value by ID.
	public function get_value_by_id($i) {
		// Init.
		$r = NULL;
		// Create PDO object
		$this->dbConnect();
		// Build prepared statement.
		if(($stmt = $this->pdo->prepare("SELECT value_txt
										 FROM tbl_values
										 WHERE value_id=:i"))) {
			// Execute.
			if($stmt->execute(array(':i' => $i))) {
				// Bind by column name.
				$stmt->bindColumn('value_txt', $value_txt);
				// Loop.
				while($stmt->fetch()) {
					// Set.
					$r = $value_txt;
				}
			}
		}
		// Return.
		return $r;
	}
	
	// Get value add info by string.
	public function get_value_add_info($s) {
		// Init.
		$r = NULL;
		// If arg sent.
		if(isset($s)) {
			// Create PDO object
			$this->dbConnect();
			// Build prepared statement.
			if(($stmt = $this->pdo->prepare("SELECT value_add_info
							 				 FROM tbl_values
							 				 WHERE value_txt=:s"))) {
				// Execute.
				if($stmt->execute(array(':s' => $s))) {
					// Bind by column name.
					$stmt->bindColumn('value_add_info', $value_add_info);
					// Loop.
					while($stmt->fetch()) {
						// Check again.
						$r = $value_add_info;
					}
				}
			}
		}
		// Return.
		return $r;
	}
	
	// Get value additional integer.
	public function get_value_add_int($s) {
		// Init.
		$r = 0;
		// If arg sent.
		if(isset($s)) {
			// Create PDO object
			$this->dbConnect();
			// Build prepared statement.
			if(($stmt = $this->pdo->prepare("SELECT value_add_int
											 FROM tbl_values
											 WHERE value_txt=:s"))) {
					// Execute.
			if($stmt->execute(array(':s' => $s))) {
				// Bind by column name.
				$stmt->bindColumn('value_add_int', $value_add_int);
				// Loop.
				while($stmt->fetch()) {
					// Check again.
					$r = $value_add_int;
				}
			}
			}
		}
		// Return.
		return $r;
	}
	
	// Get value group specific additional integer.
	public function get_specific_value_by_group_and_add_int($g, $i) {
		// Init.
		$a = array();
		// Create PDO object
		$this->dbConnect();
		// Build prepared statement.
		if(($stmt = $this->pdo->prepare("SELECT value_id, value_txt
										 FROM tbl_values
										 WHERE value_group_fk=:g AND value_add_int=:i"))) {
			// Execute.
			if($stmt->execute(array(':g' => $g, ':i' => $i))) {
				// Bind by column name.
				$stmt->bindColumn('value_id', $value_id);
				$stmt->bindColumn('value_txt', $value_txt);
				// Loop.
				while($stmt->fetch()) {
					// Build.
					$a[$value_id] = $value_txt;
				}
			}
		}
		// Return.
		return $a;
	}

	// Get full host name from ID.
	public function get_full_host_name_from_id($i) {
		// Init.
		$r = NULL;
		// Initialise.
		$serverdata = new GetServerData();
		// If arg sent.
		if(isset($i)) {
			// Create PDO object
			$this->dbConnect();
			// Build prepared statement.
			if(($stmt = $this->pdo->prepare("SELECT value_txt, value_add_info
							 				 FROM tbl_values
							 				 WHERE value_id=:i"))) {
				// Execute.
				if($stmt->execute(array(':i' => $i))) {
					// Bind by column name.
					$stmt->bindColumn('value_txt', $value_txt);
					$stmt->bindColumn('value_add_info', $value_add_info);
					// Loop.
					while($stmt->fetch()) {
						// Set.
						$r = $serverdata->set_host_name($value_txt, $value_add_info);
					}
				}
			}
		}
		// Return.
		return $r;		
	}
	
	// Get value-related ID.
	public function get_value_id($s) {
		// Init.
		$r = 0;
		// If arg sent.
		if(isset($s)) {
			// Create PDO object
			$this->dbConnect();
			// Build prepared statement.
			if(($stmt = $this->pdo->prepare("SELECT value_id
							 				 FROM tbl_values
							 				 WHERE value_txt=:s"))) {
				// Execute.
				if($stmt->execute(array(':s' => $s))) {
					// Bind by column name.
					$stmt->bindColumn('value_id', $value_id);
					// Loop.
					while($stmt->fetch()) {
						// Check again.
						$r = $value_id;
					}
				}
			}
		}
		// Return.
		return $r;
	}

	///////////////////
	// FILE-RELATED //
	/////////////////
	
	// Insert file metadata to database.
	public function insert_file_metadata($f, $format) {
		// Init.
		$r = FALSE;
		$fu = NULL;
		// Instantiate.
		$variable = new Variables();
		$serverdata = new GetServerData();
		// Get file-related variables.
		$variable->get_file_related_variables();
		// If arg passed.
		if(isset($f)) {
			// Get user ID for this user.
			$uid = $this->get_valid_user_id();
			// If valid UID is returned.
			if($uid != 0) {
				// Explode filename backwards.
				$exp = explode('.', $f);
				// Get file format ID.
				$format_id = $this->get_value_id($exp[1]);
				// Set args.
				$args = $serverdata->get_uri_args($_SESSION['default_gps_start'], $_SESSION['default_gps_stop']);
                                // Get filesize.
                                //if(!preg_match("/coalesced_json/",$f){
				//    $fs = filesize($variable->doc_root.$variable->download_dir.$f);
                                //} else {
                                $fs = filesize($variable->doc_root.$variable->download_dir.str_replace("_",".",$f));
                                //}
				// Loop through URI used in file creation and add to history.
				foreach($_SESSION['uri_deselected'] as $i => $uri) {
					// Build string.
					$fu .= ', '.$uri.$args;
				}
				// Remove first two characters from URI string.
				$fu = substr($fu, 2);
				// Get host-related ID.
				$host_id = $this->get_value_id($_SESSION['default_host']);				
				// Create PDO object
				$this->dbConnect();
				// Build prepared statement.
				if(($stmt = $this->pdo->prepare("INSERT INTO tbl_file_metadata
							 					 (file_name, file_size, file_uri_used, file_format_fk, user_fk, host_fk)
								 				 VALUES
												 (:f, :fs, :fu, :format_id, :uid, :h)"))) {
					// Execute.
					if($stmt->execute(array(':f' => $f, ':fs' => $fs, ':fu' => $fu, ':format_id' => $format_id, ':uid' => $uid, ':h' => $host_id))) {
						// Set.
						$r = TRUE;
					}
				}
			}
		}
		// Return.
		return $r;
	}

	// Get recent query results.
	public function get_recent_query_results($limit, $home, $tabs) {
		// Init.
		$r = NULL;
		$i = 0;
		$limit_s = 0;
		$limit_str = NULL;
		$tot_output = 0;
		// Instantiate.
		$variable = new Variables();
		$structure = new GetStructure();
		// Get file-related variables.
		$variable->get_file_related_variables();
		// Get app-related variables.
		$variable->get_app_variables();
		// Get content-call ID.
		$variable->getContentCallID();
		// Add number of tabs required.
	 	$structure->getRequiredTabs($tabs);
	 	// Sort ascending/descending.
		$date_ad = 'asc';
		$data_ad = 'asc';
		$uri_ad = 'asc';
		$size_ad = 'asc';
		$user_ad = 'asc';
		$format_ad = 'asc';
		$date_ar = NULL;
		$data_ar = NULL;
		$uri_ar = NULL;
		$size_ar = NULL;
		$format_ar = NULL;
		$user_ar = NULL;
	 	if(isset($_GET['date_ad']) || isset($_GET['data_ad']) || isset($_GET['uri_ad']) || isset($_GET['size_ad']) || isset($_GET['format_ad']) || isset($_GET['user_ad'])) {
			if(isset($_GET['date_ad'])) {
				// Set ORDER BY SQL.
			 	$o = 'file_created '.strtoupper($_GET['date_ad']);
			 	// Set output.
			 	if($_GET['date_ad'] == 'asc') {
			 		$date_ad = 'desc';
			 	}
			 	$date_ar = "<img class=\"img_sort_arrow\" src=\"images/arrow_".strtolower($_GET['date_ad']).".png\" alt=\"Sorting ".strtolower($_GET['date_ad'])."ending\" title=\"Sorting ".strtolower($_GET['date_ad'])."ending\" />";
		 	}
	 		if(isset($_GET['data_ad'])) {
				// Set ORDER BY SQL.
			 	$o = 'value_add_info '.strtoupper($_GET['data_ad']);
			 	// Set output.
			 	if($_GET['data_ad'] == 'asc') {
			 		$data_ad = 'desc';
			 	}
			 	$data_ar = "<img class=\"img_sort_arrow\" src=\"images/arrow_".strtolower($_GET['data_ad']).".png\" alt=\"Sorting ".strtolower($_GET['data_ad'])."ending\" title=\"Sorting ".strtolower($_GET['data_ad'])."ending\" />";
	 		}
		 	if(isset($_GET['uri_ad'])) {
		 		// Set ORDER BY SQL.
		 		$o = 'file_uri_used '.strtoupper($_GET['uri_ad']);
		 		// Set output.
		 		if($_GET['uri_ad'] == 'asc') {
		 			$uri_ad = 'desc';
		 		}
			 	$uri_ar = "<img class=\"img_sort_arrow\" src=\"images/arrow_".strtolower($_GET['uri_ad']).".png\" alt=\"Sorting ".strtolower($_GET['uri_ad'])."ending\" title=\"Sorting ".strtolower($_GET['uri_ad'])."ending\" />";
		 	}
	 		if(isset($_GET['size_ad'])) {
		 		// Set ORDER BY SQL.
		 		$o = 'file_size '.strtoupper($_GET['size_ad']);
		 		// Set output.
		 		if($_GET['size_ad'] == 'asc') {
		 			$size_ad = 'desc';
		 		}
			 	$size_ar = "<img class=\"img_sort_arrow\" src=\"images/arrow_".strtolower($_GET['size_ad']).".png\" alt=\"Sorting ".strtolower($_GET['size_ad'])."ending\" title=\"Sorting ".strtolower($_GET['size_ad'])."ending\" />";
	 		}
	 		if(isset($_GET['format_ad'])) {
		 		// Set ORDER BY SQL.
		 		$o = 'formats.file_format '.strtoupper($_GET['format_ad']);
		 		// Set output.
		 		if($_GET['format_ad'] == 'asc') {
		 			$format_ad = 'desc';
		 		}
			 	$format_ar = "<img class=\"img_sort_arrow\" src=\"images/arrow_".strtolower($_GET['format_ad']).".png\" alt=\"Sorting ".strtolower($_GET['format_ad'])."ending\" title=\"Sorting ".strtolower($_GET['format_ad'])."ending\" />";
	 		}
	 		if(isset($_GET['user_ad'])) {
		 		// Set ORDER BY SQL.
		 		$o = 'users.username '.strtoupper($_GET['user_ad']);
		 		// Set output.
		 		if($_GET['user_ad'] == 'asc') {
		 			$user_ad = 'desc';
		 		}
			 	$user_ar = "<img class=\"img_sort_arrow\" src=\"images/arrow_".strtolower($_GET['user_ad']).".png\" alt=\"Sorting ".strtolower($_GET['user_ad'])."ending\" title=\"Sorting ".strtolower($_GET['user_ad'])."ending\" />";
	 		}
	 	}
	 	else {
	 		$o = 'file_id DESC ';
	 	}
	 	// Set WHERE SQL clause.
		$w_sql = NULL;
		// If not on homepage.
		if(!$home) {
			// Filter for user.
			if(isset($_SESSION['filter_user']) && !empty($_SESSION['filter_user']) && $_SESSION['filter_user'] != 0) {
				$w_sql .= " AND user_fk=".$_SESSION['filter_user'];
			}
			// Filter for dataset.
			if(isset($_SESSION['filter_data']) && !empty($_SESSION['filter_data']) && $_SESSION['filter_data'] != 0) {
				$w_sql .= " AND host_fk=".$_SESSION['filter_data'];
			}
			// If WHERE SQL clause has been set.
			if(!empty($w_sql)) {
				$w_sql = "WHERE ".substr($w_sql, 4);
			}
		}
		// Add break.
		$structure->getBreak($tabs+1);
		$r .= $structure->brk;
		// Create PDO object
		$this->dbConnect();
		// Get total number of payloads.
		if(($stmt = $this->pdo->prepare("SELECT COUNT(file_id) AS 'tot'
										 FROM tbl_file_metadata ".$w_sql))) {
			// Execute.
			if($stmt->execute()) {
				// Bind by column name.
				$stmt->bindColumn('tot', $tot);
				// Loop.
				while($stmt->fetch()) {
					$tot_output = $tot;
				}
			}
		}
		// If not on homepage.
		if(!$home) {
			// Set start and end display values.
			$s = (($_SESSION['filter_start_page']-1) * $variable->payloads_to_display) + 1;
			$e = ($s + $variable->payloads_to_display) - 1;
			// Set total number of pages to be used.
			$t = round($tot_output/$variable->payloads_to_display);
			// If the end display value is above the total.
			if($e > $tot_output) {
				// Re-set it to the total.
				$e = $tot_output;
			}
			// Set SQL LIMIT start.
			$limit_s = $s-1;
			// Output totals.
			$r .= $structure->tabStr."<p>Displaying <strong>".$s."</strong> to <strong>".$e."</strong> of <strong>".$tot_output."</strong> payloads</p>\n";
			// Output Start link.
			if($_SESSION['filter_start_page'] > ($variable->payloads_page_counter_display_diff+1)) {
				// Set Start link.
				$r .= $structure->tabStr."<p id=\"filter_page_no_start\" class=\"filter_page_no\" onclick=\"set_filter_start_page_no(1)\">START</p>\n";
			}
			// Set pages.
			for($i=1; $i<=$t; $i++) {
				// Set formatted page.
				$i_fmt = $i;
				// If currently selected page.
				if($i == $_SESSION['filter_start_page']) {
					$i_fmt = "<strong>".$i."</strong>";
				}
				// Display those pages within n either way of the existing page number.
				if(($_SESSION['filter_start_page'] > $variable->payloads_page_counter_display_diff
					&& $i >= ($_SESSION['filter_start_page']-$variable->payloads_page_counter_display_diff)
					&& $i <= ($_SESSION['filter_start_page']+$variable->payloads_page_counter_display_diff))
				|| ($_SESSION['filter_start_page'] <= $variable->payloads_page_counter_display_diff
					&& $i <= ($variable->payloads_page_counter_display_diff*2))
				|| ($_SESSION['filter_start_page'] >= $t-$variable->payloads_page_counter_display_diff
					&& $i >= $t-($variable->payloads_page_counter_display_diff*2))) {
					// Add pages to output.
					$r .= $structure->tabStr."<p id=\"filter_page_no_start\" class=\"filter_page_no\" onclick=\"set_filter_start_page_no(".$i.")\">".$i_fmt."</p>\n";
				}
			}
			// Output End link.
			if($_SESSION['filter_start_page'] < ($i-$variable->payloads_page_counter_display_diff-1)) {
				// Set End link.
				$r .= $structure->tabStr."<p id=\"filter_page_no_start\" class=\"filter_page_no\" onclick=\"set_filter_start_page_no(".$t.")\">END</p>\n";
			}
		}
		// Set limit.
		if(!empty($limit) && $limit > 0) {
			$limit_str = " LIMIT ".$limit_s.",".$limit;
		}
		// Open table.
		$r .= $structure->tabStr."<table cellpadding=\"0\" cellspacing=\"1\" border=\"0\" id=\"tbl_query_results\">\n";
		// Headings.
		$r .= $structure->tabStr."	<tr>\n";
		$r .= $structure->tabStr."		<td class=\"query_results_hdr\"><a href=\"?c=".$variable->c."&date_ad=".$date_ad."\">Date / Time</a>".$date_ar."</td>\n";
		$r .= $structure->tabStr."		<td class=\"query_results_hdr\"><a href=\"?c=".$variable->c."&data_ad=".$data_ad."\">Data</a>".$data_ar."</td>\n";
		$r .= $structure->tabStr."		<td class=\"query_results_hdr\"><a href=\"?c=".$variable->c."&uri_ad=".$uri_ad."\">URI used</a>".$uri_ar."</td>\n";
		$r .= $structure->tabStr."		<td class=\"query_results_hdr\"><a href=\"?c=".$variable->c."&size_ad=".$size_ad."\">File size</a>".$size_ar."</td>\n";
		$r .= $structure->tabStr."		<td class=\"query_results_hdr\"><a href=\"?c=".$variable->c."&format_ad=".$format_ad."\">File format</a>".$format_ar."</td>\n";
		$r .= $structure->tabStr."		<td class=\"query_results_hdr\"><a href=\"?c=".$variable->c."&user_ad=".$user_ad."\">User</a>".$user_ar."</td>\n";
		$r .= $structure->tabStr."	</tr>\n";
		// Set URI class.
		$uri_class = NULL;
		// If on the homepage.
		if($home) {
			// Reset URI class.
			$uri_class = " class=\"a_small\"";
		}
		// Build prepared statement.
		if(($stmt = $this->pdo->prepare("SELECT tbl_file_metadata.*, tbl_values.*, DATE_FORMAT(file_created, '%Y-%m-%d %H:%i') AS 'file_created_fmt', users.username, formats.file_format
										 FROM tbl_file_metadata
										 LEFT join tbl_values ON tbl_file_metadata.host_fk = tbl_values.value_id
										 LEFT join (
										 SELECT value_id AS user_id, value_txt AS username FROM tbl_values
										 WHERE value_group_fk=3) AS users ON tbl_file_metadata.user_fk = users.user_id
										 LEFT join (
										 SELECT value_id AS file_format_id, value_txt AS file_format FROM tbl_values
										 WHERE value_group_fk=4) AS formats ON tbl_file_metadata.file_format_fk = formats.file_format_id
										 ".$w_sql."
										 ORDER BY ".$o.$limit_str))) {
			// Execute.
			if($stmt->execute()) {
				// Bind by column name.
				$stmt->bindColumn('file_name', $file_name);
				$stmt->bindColumn('file_size', $file_size);
 				$stmt->bindColumn('file_uri_used', $file_uri_used);
 				$stmt->bindColumn('value_add_info', $data);
 				$stmt->bindColumn('file_created_fmt', $file_created_fmt);
				$stmt->bindColumn('user_fk', $user_fk);
				$stmt->bindColumn('file_format_fk', $file_format_fk);
				$stmt->bindColumn('file_format', $file_format);
				// Loop.
				while($stmt->fetch()) {
					// Set bg.
					$i++;
					$c = NULL;
					if($i == 2) {
						$c = "_hl";
						$i = 0;
					}
					// Set filesize for output.
					$suffix = "K";
					if($file_size > 999999) {
						$suffix = "M";
						$file_size = $file_size/1000000;
					}
					else {
						$file_size = $file_size/1000;
					}
					// Round to 1 decimal place.
					$file_size = round($file_size, 1);
					// Get username.
					$username = str_replace('@', '<br />@', $this->get_username($user_fk));
					// Re-set file format, removing underscore.
					$file_format = str_replace('_', ' ', $file_format);
					// Set.
					$r .= $structure->tabStr."	<tr>\n";
					$r .= $structure->tabStr."		<td class=\"query_results".$c."\">".$file_created_fmt."</td>\n";
					$r .= $structure->tabStr."		<td class=\"query_results".$c."\">".$data."</td>\n";
					$r .= $structure->tabStr."		<td class=\"query_results".$c."\"><a href=\"".$variable->download_dir.$file_name."\" target=\"_blank\"".$uri_class.">".str_replace(", ", "<br />\n", $file_uri_used)."</a></td>\n";
					$r .= $structure->tabStr."		<td class=\"query_results".$c."\">".$file_size." ".$suffix."B</td>\n";
					$r .= $structure->tabStr."		<td class=\"query_results".$c."\">".$file_format."</td>\n";
					$r .= $structure->tabStr."		<td class=\"query_results".$c."\">".$username."</td>\n";
					$r .= $structure->tabStr."	</tr>\n";
				}
			}
		}
		// Close table.
		$r .= $structure->tabStr."</table>\n";
		// Return.
		return $r;
	}
	
	////////////////////////////
	// RTS-RELATED FUNCTIONS //
	//////////////////////////
	
	// Get test runs.
	public function get_recent_regression_test_runs($limit, $home, $tabs) {
		// Init.
		$r = NULL;
		$i = 0;
		$limit_s = 0;
		$limit_str = NULL;
		$tot_output = 0;
		// Instantiate.
		$variable = new Variables();
		$structure = new GetStructure();
		// Get app-related variables.
		$variable->get_app_variables();
		// Get content-call ID.
		$variable->getContentCallID();
		// Add number of tabs required.
		$structure->getRequiredTabs($tabs);
		$dataset_ad = 'asc';
		$date_start_ad = 'asc';
		$date_stop_ad = 'asc';
		$failures_ad = 'asc';
		$dataset_ar = NULL;
		$date_start_ar = NULL;
		$date_stop_ar = NULL;
		$failures_ar = NULL;
		// If ordering.
		if(isset($_GET['date_start_ad']) || isset($_GET['date_stop_ad']) || isset($_GET['failures_ad']) || isset($_GET['dataset_ad'])) {
			// If dataset ordering is set.
			if(isset($_GET['dataset_ad'])) {
				// Set ORDER BY SQL.
			 	$o = 'dataset '.strtoupper($_GET['dataset_ad']);
			 	// Set output.
			 	if($_GET['dataset_ad'] == 'asc') {
			 		$dataset_ad = 'desc';
			 	}
			 	$dataset_ar = "<img class=\"img_sort_arrow\" src=\"images/arrow_".strtolower($_GET['dataset_ad']).".png\" alt=\"Sorting ".strtolower($_GET['dataset_ad'])."ending\" title=\"Sorting ".strtolower($_GET['dataset_ad'])."ending\" />";
		 	}
			// If start date ordering is set.
			if(isset($_GET['date_start_ad'])) {
				// Set ORDER BY SQL.
			 	$o = 'test_run_start_time '.strtoupper($_GET['date_start_ad']);
			 	// Set output.
			 	if($_GET['date_start_ad'] == 'asc') {
			 		$date_start_ad = 'desc';
			 	}
			 	$date_start_ar = "<img class=\"img_sort_arrow\" src=\"images/arrow_".strtolower($_GET['date_start_ad']).".png\" alt=\"Sorting ".strtolower($_GET['date_start_ad'])."ending\" title=\"Sorting ".strtolower($_GET['date_start_ad'])."ending\" />";
		 	}
		 	// If stop date ordering is set.
			if(isset($_GET['date_stop_ad'])) {
				// Set ORDER BY SQL.
			 	$o = 'test_run_stop_time '.strtoupper($_GET['date_stop_ad']);
			 	// Set output.
			 	if($_GET['date_stop_ad'] == 'asc') {
			 		$date_stop_ad = 'desc';
			 	}
			 	$date_stop_ar = "<img class=\"img_sort_arrow\" src=\"images/arrow_".strtolower($_GET['date_stop_ad']).".png\" alt=\"Sorting ".strtolower($_GET['date_stop_ad'])."ending\" title=\"Sorting ".strtolower($_GET['date_stop_ad'])."ending\" />";
		 	}
	 	 	// If failures ordering is set.
			if(isset($_GET['failures_ad'])) {
				// Set ORDER BY SQL.
			 	$o = 'test_run_failures '.strtoupper($_GET['failures_ad']);
			 	// Set output.
			 	if($_GET['failures_ad'] == 'asc') {
			 		$failures_ad = 'desc';
			 	}
			 	$failures_ar = "<img class=\"img_sort_arrow\" src=\"images/arrow_".strtolower($_GET['failures_ad']).".png\" alt=\"Sorting ".strtolower($_GET['failures_ad'])."ending\" title=\"Sorting ".strtolower($_GET['failures_ad'])."ending\" />";
		 	}
	 	}
		else {
	 		$o = 'test_run_id DESC ';
	 	}
	 	// Create PDO object
		$this->db_rts_connect();
		// Get total number of tests.
		if(($stmt = $this->pdo_rts->prepare("SELECT COUNT(test_run_id) AS 'tot'
										 	 FROM tbl_test_runs"))) {
			// Execute.
			if($stmt->execute()) {
				// Bind by column name.
				$stmt->bindColumn('tot', $tot);
				// Loop.
				while($stmt->fetch()) {
					$tot_output = $tot;
				}
			}
		}
		// Set start and end display values.
		$s = (($_SESSION['rts_filter_start_page']-1) * $variable->rts_to_display) + 1;
		$e = ($s + $variable->rts_to_display) - 1;
		// Set total number of pages to be used.
		$t = round($tot_output/$variable->rts_to_display);
		// If the end display value is above the total.
		if($e > $tot_output) {
			// Re-set it to the total.
			$e = $tot_output;
		}
		// Set SQL LIMIT start.
		$limit_s = $s-1;
		// Output totals.
		$r .= $structure->tabStr."<p>Displaying <strong>".$s."</strong> to <strong>".$e."</strong> of <strong>".$tot_output."</strong> test runs</p>\n";
		// Set pages.
		for($i=1; $i<=$t; $i++) {
			// Set formatted page.
			$i_fmt = $i;
			// If currently selected page.
			if($i == $_SESSION['rts_filter_start_page']) {
				$i_fmt = "<strong>".$i."</strong>";
			}
			// Add pages to output.
			$r .= $structure->tabStr."<p id=\"rts_filter_page_no_start\" class=\"filter_page_no\" onclick=\"set_rts_filter_start_page_no(".$i.")\">".$i_fmt."</p>\n";
		}
		// Set limit.
		if(!empty($limit) && $limit > 0) {
			$limit_str = " LIMIT ".$limit_s.",".$limit;
		}
		// Open table.
		$r .= $structure->tabStr."<table cellpadding=\"0\" cellspacing=\"1\" border=\"0\" id=\"tbl_test_results\">\n";
		// Headings.
		$r .= $structure->tabStr."	<tr>\n";
		$r .= $structure->tabStr."		<td class=\"query_results_hdr\"><a href=\"?c=".$variable->c."&dataset_ad=".$dataset_ad."\">Dataset</a>".$dataset_ar."</td>\n";
		$r .= $structure->tabStr."		<td class=\"query_results_hdr\"><a href=\"?c=".$variable->c."&date_start_ad=".$date_start_ad."\">Start time</a>".$date_start_ar."</td>\n";
		$r .= $structure->tabStr."		<td class=\"query_results_hdr\"><a href=\"?c=".$variable->c."&date_stop_ad=".$date_stop_ad."\">Stop time</a>".$date_stop_ar."</td>\n";
		$r .= $structure->tabStr."		<td class=\"query_results_hdr\"><a href=\"?c=".$variable->c."&failures_ad=".$failures_ad."\">Failures</a>".$failures_ar."</td>\n";
		$r .= $structure->tabStr."	</tr>\n";
		// Build prepared statement.
		if(($stmt = $this->pdo_rts->prepare("SELECT *
											 FROM tbl_test_runs
											 LEFT join (
											 SELECT value_id AS dataset_id, CONCAT(value_add_info, ' data (', value_txt, ')') AS dataset FROM tbl_values
											 WHERE value_group_fk=4) AS datasets ON tbl_test_runs.dataset_fk = datasets.dataset_id
											 ORDER BY ".$o.$limit_str))) {
			// Execute.
			if($stmt->execute()) {
				// Bind by column name.
				$stmt->bindColumn('test_run_id', $test_run_id);
				$stmt->bindColumn('dataset', $dataset);
				$stmt->bindColumn('test_run_start_time', $test_run_start_time);
				$stmt->bindColumn('test_run_stop_time', $test_run_stop_time);
				$stmt->bindColumn('test_run_failures', $test_run_failures);
				// Loop.
				while($stmt->fetch()) {
					// Set.
					$c = NULL;
					$img = NULL;
					// Set bg.
					$i++;
					$c = NULL;
					if($i == 2) {
						$c = "_hl";
						$i = 0;
					}
					// If failures were thrown up.
					if($test_run_failures > 0) {
						// Set different style call.
						$c = "_error";
					}
					// If the run is underway.
					if(empty($test_run_stop_time)) {
						// Set image.
						$img = "<img src=\"images/retrieving_segments_mini.gif\" alt=\"Test Run currently underway\" title=\"Test Run currently underway\" /> ";
					}
					// Set.
					$r .= $structure->tabStr."	<tr>\n";
					$r .= $structure->tabStr."		<td class=\"query_results".$c."\"><a href=\"?c=".$variable->c."&r=".$test_run_id."\">".$img.$dataset."</a></td>\n";
					$r .= $structure->tabStr."		<td class=\"query_results".$c."\"><a href=\"?c=".$variable->c."&r=".$test_run_id."\">".$test_run_start_time."</a></td>\n";
					$r .= $structure->tabStr."		<td class=\"query_results".$c."\"><a href=\"?c=".$variable->c."&r=".$test_run_id."\">".$test_run_stop_time."</a></td>\n";
					$r .= $structure->tabStr."		<td class=\"query_results".$c."\"><a href=\"?c=".$variable->c."&r=".$test_run_id."\">".$test_run_failures."</a></td>\n";
					$r .= $structure->tabStr."	</tr>\n";
				}
			}
		}
		// Close table.
		$r .= $structure->tabStr."</table>\n";
		// Return.
		return $r;
	}
	
	// Get five test runs for the homepage.
	public function get_last_five_test_runs_for_homepage($tabs) {
		// Init.
		$r = NULL;
		// Instantiate.
		$variable = new Variables();
		$structure = new GetStructure();
		// Add number of tabs required.
		$structure->getRequiredTabs($tabs);
	 	// Create PDO object
		$this->db_rts_connect();
		// Open table.
		$r .= $structure->tabStr."<table cellpadding=\"0\" cellspacing=\"1\" border=\"0\" id=\"tbl_query_results\">\n";
		// Headings.
		$r .= $structure->tabStr."	<tr>\n";
		$r .= $structure->tabStr."		<td class=\"query_results_hdr\">Start time</td>\n";
		$r .= $structure->tabStr."		<td class=\"query_results_hdr\">Failures</td>\n";
		$r .= $structure->tabStr."	</tr>\n";
		// Build prepared statement.
		if(($stmt = $this->pdo_rts->prepare("SELECT *
											 FROM tbl_test_runs
											 LEFT join (
											 SELECT value_id AS dataset_id, CONCAT(value_add_info, ' data (', value_txt, ')') AS dataset FROM tbl_values
											 WHERE value_group_fk=4) AS datasets ON tbl_test_runs.dataset_fk = datasets.dataset_id
											 ORDER BY test_run_id DESC
											 LIMIT 5"))) {
			// Execute.
			if($stmt->execute()) {
				// Bind by column name.
				$stmt->bindColumn('test_run_id', $test_run_id);
				$stmt->bindColumn('dataset', $dataset);
				$stmt->bindColumn('test_run_start_time', $test_run_start_time);
				$stmt->bindColumn('test_run_stop_time', $test_run_stop_time);
				$stmt->bindColumn('test_run_failures', $test_run_failures);
				// Loop.
				while($stmt->fetch()) {
					// Set.
					$c = NULL;
					$img = NULL;
					// If failures were thrown up.
					if($test_run_failures > 0) {
						// Set different style call.
						$c = "_error";
					}
					// If the run is underway.
					if(empty($test_run_stop_time)) {
						// Set image.
						$img = "<img src=\"images/retrieving_segments_mini.gif\" alt=\"Test Run currently underway\" title=\"Test Run currently underway\" /> ";
					}
					// Set.
					$r .= $structure->tabStr."	<tr>\n";
					$r .= $structure->tabStr."		<td class=\"query_results".$c."\"><a href=\"?c=40&r=".$test_run_id."\">".$img.$test_run_start_time."</a></td>\n";
					$r .= $structure->tabStr."		<td class=\"query_results".$c."\"><a href=\"?c=40&r=".$test_run_id."\">".$test_run_failures."</a></td>\n";
					$r .= $structure->tabStr."	</tr>\n";
				}
			}
		}
		// Close table.
		$r .= $structure->tabStr."</table>\n";
		// Return.
		return $r;
	}
	
	// Get a specific regression test.
	public function specific_regression_test($rt, $tabs) {
		// Init.
		$r = NULL;
		// Instantiate.
		$structure = new GetStructure();
		$variable = new Variables();
		// Add number of tabs required.
		$structure->getRequiredTabs($tabs);
		// Get content-call ID.
		$variable->getContentCallID();
		// If not RT passed.
		if(!isset($rt)) {
			// Set error message.
			$r .= $structure->tabStr."<p>There are no available component-interface and data-integrity test results for this run.</p>\n";
		}
		else {
		 	// Create PDO object
			$this->db_rts_connect();
			// Get RT info.
			if(($stmt = $this->pdo_rts->prepare("SELECT *
												 FROM tbl_test_runs
												 WHERE test_run_id=:rt
												 LIMIT 1"))) {
				// Execute.
				if($stmt->execute(array('rt' => $rt))) {
					// Bind by column name.
					$stmt->bindColumn('test_run_start_time', $test_run_start_time);
					$stmt->bindColumn('test_run_stop_time', $test_run_stop_time);
					$stmt->bindColumn('test_run_failures', $test_run_failures);
					// Loop.
					while($stmt->fetch()) {
						// Set.
						$r .= $structure->tabStr."<h4>Component-Interface and Data-Integrity Run Details</h4>\n";
						$r .= $structure->tabStr."<p><img alt=\"\" title=\"\" src=\"images/arrow_on_blue.png\" /><a href=\"?c=".$variable->c."\"> Return to list of component-interface and data-integrity test runs</a>.</p>\n";
						$r .= $structure->tabStr."<p>Currently viewing details of component-interface and data-integrity test run started at <strong>".$test_run_start_time."</strong> and ended at <strong>".$test_run_stop_time."</strong>. This run contained <strong>".$test_run_failures."</strong> failures. N.B. Any failures are highlighted in <font class=\"p_query_results_error\">red</font>.</p>\n";
					}
				}
			}
			// Open table.
			$r .= $structure->tabStr."<table cellpadding=\"0\" cellspacing=\"1\" border=\"0\" id=\"tbl_query_results\">\n";
			// Headings.
			$r .= $structure->tabStr."	<tr>\n";
			$r .= $structure->tabStr."		<td class=\"query_results_hdr\"><strong>Date/Time</strong></td>\n";
			$r .= $structure->tabStr."		<td class=\"query_results_hdr\"><strong>Test name</strong></td>\n";
			$r .= $structure->tabStr."		<td class=\"query_results_hdr\"><strong>Details</strong></td>\n";
			$r .= $structure->tabStr."	</tr>\n";
			// Build prepared statement.
			if(($stmt = $this->pdo_rts->prepare("SELECT *
												 FROM tbl_test_results
												 LEFT JOIN tbl_values ON tbl_test_results.test_name_fk = tbl_values.value_id
												 WHERE test_run_fk=:rt"))) {
				// Execute.
				if($stmt->execute(array(':rt' => $rt))) {
					// Bind by column name.
					$stmt->bindColumn('test_result_id', $test_result_id);
					$stmt->bindColumn('value_txt', $test_name);
					$stmt->bindColumn('test_success_level_fk', $test_success_level_fk);
					$stmt->bindColumn('test_details', $test_details);
					$stmt->bindColumn('test_time', $test_time);
					// Loop.
					while($stmt->fetch()) {
						// Set bg.
						$c = NULL;
						if($test_success_level_fk == 4) {
							$c = "_error";
						}
						// Set.
						$r .= $structure->tabStr."	<tr>\n";
						$r .= $structure->tabStr."		<td class=\"query_results".$c."\">".$test_time."</td>\n";
						$r .= $structure->tabStr."		<td class=\"query_results".$c."\">".$test_name."</td>\n";
						$r .= $structure->tabStr."		<td class=\"query_results".$c."\">".str_replace("u'", "<br />'", $test_details)."</td>\n";
						$r .= $structure->tabStr."	</tr>\n";
					}
				}
			}
		}
		// Close table.
		$r .= $structure->tabStr."</table>\n";
		// Return.
		return $r;
	}
	

	/////////////////////////////
	// USER-RELATED FUNCTIONS //
	///////////////////////////	
	// Get user ID for this user.
	private function get_valid_user_id() {
		// Init.
		$r = 0;
		// If the username is set.
		if(isset($_SERVER['eduPersonPrincipalName']) && !empty($_SERVER['eduPersonPrincipalName'])) {
			// Get the ID for this user.
			$r = $this->get_user_id($_SERVER['eduPersonPrincipalName']);
			// If no user found.
			if($r == 0) {
				// Insert user to database.
				if($this->insert_user($_SERVER['eduPersonPrincipalName'])) {
					// Attempt again to get the ID for this user.
					$r = $this->get_user_id($_SERVER['eduPersonPrincipalName']);
				}
			}
		}
		// Return.
		return $r;
	}
	
	// Get the ID for this user.
	private function get_user_id($s) {
		// Init.
		$r = 0;
		// If arg sent.
		if(isset($s)) {
			// Create PDO object
			$this->dbConnect();
			// Build prepared statement.
			if(($stmt = $this->pdo->prepare("SELECT value_id
							 				 FROM tbl_values
							 				 WHERE value_group_fk=3 AND value_txt=:s"))) {
				// Execute.
				if($stmt->execute(array(':s' => $s))) {
					// Bind by column name.
					$stmt->bindColumn('value_id', $value_id);
					// Loop.
					while($stmt->fetch()) {
						// Set.
						$r = $value_id;
					}
				}
			}
		}
		// Return.
		return $r;
	}
	
	// Get username from ID.
	private function get_username($i) {
		// Init.
		$r = 0;
		// If arg sent.
		if(isset($i)) {
			// Create PDO object
			$this->dbConnect();
			// Build prepared statement.
			if(($stmt = $this->pdo->prepare("SELECT value_txt
							 				 FROM tbl_values
							 				 WHERE value_group_fk=3 AND value_id=:i"))) {
				// Execute.
				if($stmt->execute(array(':i' => $i))) {
					// Bind by column name.
					$stmt->bindColumn('value_txt', $value_txt);
					// Loop.
					while($stmt->fetch()) {
						// Set.
						$r = $value_txt;
					}
				}
			}
		}
		// Return.
		return $r;
	}
	
	// Insert username.
	public function insert_user($s) {
		// Init.
		$r = FALSE;
		// If arg passed.
		if(isset($s)) {
			// If user does not already exist.
			if($this->get_user_id($s) == 0) {
				// Create PDO object
				$this->dbConnect();
				// Build prepared statement.
				if(($stmt = $this->pdo->prepare("INSERT INTO tbl_values
							 					 (value_group_fk, value_txt)
								 				 VALUES
												 (3, :s)"))) {
					// Execute.
					if($stmt->execute(array(':s' => $s))) {
						// Set.
						$r = TRUE;
					}
				}
			}
		}
		// Return.
		return $r;
	}
	
	///////////////////////////////
	// BACKUP-RELATED FUNCTIONS //
	/////////////////////////////
	
	// Get total number of backups available.
	public function get_backup_total() {
		// Init.
		$r = 0;
		// Create PDO object
		$this->db_rts_connect();
		// Build prepared statement.
		if(($stmt = $this->pdo_rts->prepare("SELECT COUNT(backup_id) AS 'tot'
										 	 FROM tbl_backups "))) {
			// Execute.
			if($stmt->execute()) {
				// Bind by column name.
				$stmt->bindColumn('tot', $tot);
				// Loop.
				while($stmt->fetch()) {
					// Set.
					$r = $tot;
				}
			}
		}
		// Return.
		return $r;
	}
	
	// Get backup array.
	public function get_backup_array($o, $limit_str) {
		// Init.
		$a = array();
		// Create PDO object
		$this->db_rts_connect();
		// Build prepared statement.
		if(($stmt = $this->pdo_rts->prepare("SELECT *, TIMEDIFF(export_time_stop, export_time_start) AS 'export_duration', TIMEDIFF(import_time_stop, import_time_start) AS 'import_duration', ADDTIME(TIMEDIFF(export_time_stop, export_time_start), TIMEDIFF(import_time_stop, import_time_start)) AS 'total_duration'
										 	 FROM tbl_backups
										 	 ORDER BY ".$o.$limit_str))) {
			// Execute.
			if($stmt->execute()) {
				// Bind by column name.
				$stmt->bindColumn('backup_id', $backup_id);
				$stmt->bindColumn('backup_date', $backup_date);
				$stmt->bindColumn('export_time_start', $export_time_start);
				$stmt->bindColumn('export_time_stop', $export_time_stop);
				$stmt->bindColumn('export_duration', $export_duration);
				$stmt->bindColumn('import_time_start', $import_time_start);
				$stmt->bindColumn('import_time_stop', $import_time_stop);
				$stmt->bindColumn('import_duration', $import_duration);
				$stmt->bindColumn('total_duration', $total_duration);
				// Loop.
				while($stmt->fetch()) {
					// Set.
					$a[$backup_id] = array('backup_date' => $backup_date,
										   'export_time_start' => $export_time_start,
										   'export_time_stop' => $export_time_stop,
										   'export_duration' => $export_duration,
										   'import_time_start' => $import_time_start,
										   'import_time_stop' => $import_time_stop,
										   'import_duration' => $import_duration,
										   'total_duration' => $total_duration);
				}
			}
		}
		// Return.
		return $a;
	}

}

?>
