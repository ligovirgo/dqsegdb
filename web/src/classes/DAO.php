<?php

// Get libraries.
require_once('InitVar.php');

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
	public function insert_file_metadata($f) {
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
				// Set args.
				$args = $serverdata->get_uri_args($_SESSION['default_gps_start'], $_SESSION['default_gps_stop']);
				// Get filesize.
				$fs = filesize($variable->doc_root.$variable->download_dir.$f);
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
							 					 (file_name, file_size, file_uri_used, user_fk, host_fk)
								 				 VALUES
												 (:f, :fs, :fu, :uid, :h)"))) {
					// Execute.
					if($stmt->execute(array(':f' => $f, ':fs' => $fs, ':fu' => $fu, ':uid' => $uid, ':h' => $host_id))) {
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
	public function get_recent_query_results($tabs) {
		// Init.
		$r = NULL;
		$i = 0;
		// Instantiate.
		$variable = new Variables();
		$structure = new GetStructure();
		// Get file-related variables.
		$variable->get_file_related_variables();
		// Add number of tabs required.
	 	$structure->getRequiredTabs($tabs);
		// Open table.
		$r .= $structure->tabStr."<table cellpadding=\"0\" cellspacing=\"1\" border=\"0\" id=\"tbl_query_results\">\n";
		// Headings.
		$r .= $structure->tabStr."	<tr>\n";
		$r .= $structure->tabStr."		<td class=\"query_results_hdr\">Date / Time</td>\n";
		$r .= $structure->tabStr."		<td class=\"query_results_hdr\">Data</td>\n";
		$r .= $structure->tabStr."		<td class=\"query_results_hdr\">URI used</td>\n";
		$r .= $structure->tabStr."		<td class=\"query_results_hdr\">File size</td>\n";
		$r .= $structure->tabStr."		<td class=\"query_results_hdr\">User</td>\n";
		$r .= $structure->tabStr."	</tr>\n";
		// Create PDO object
		$this->dbConnect();
		// Build prepared statement.
		if(($stmt = $this->pdo->prepare("SELECT *, DATE_FORMAT(file_created, '%Y-%m-%d %H:%i') AS 'file_created_fmt'
										 FROM tbl_file_metadata
										 LEFT JOIN tbl_values ON tbl_file_metadata.host_fk = tbl_values.value_id
										 ORDER BY file_id DESC
										 LIMIT 5"))) {
			// Execute.
			if($stmt->execute()) {
				// Bind by column name.
				$stmt->bindColumn('file_name', $file_name);
				$stmt->bindColumn('file_size', $file_size);
 				$stmt->bindColumn('file_uri_used', $file_uri_used);
 				$stmt->bindColumn('value_add_info', $data);
 				$stmt->bindColumn('file_created_fmt', $file_created_fmt);
				$stmt->bindColumn('user_fk', $user_fk);
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
					// Set.
					$r .= $structure->tabStr."	<tr>\n";
					$r .= $structure->tabStr."		<td class=\"query_results".$c."\">".$file_created_fmt."</td>\n";
					$r .= $structure->tabStr."		<td class=\"query_results".$c."\">".$data."</td>\n";
					$r .= $structure->tabStr."		<td class=\"query_results".$c."\"><a href=\"".$variable->download_dir.$file_name."\" target=\"_blank\">".str_replace(", ", "<br />\n", $file_uri_used)."</a></td>\n";
					$r .= $structure->tabStr."		<td class=\"query_results".$c."\">".$file_size." ".$suffix."B</td>\n";
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
	
}

?>