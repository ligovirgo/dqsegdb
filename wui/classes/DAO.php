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
	public function dbConnect()
	{
		// Create new variables object.
		$variable = new Variables();
		$variable->initVariables();
		// If connection not made.
		if(!$this->pdo)
		{
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
	public function getTopLinkSQL()
	{
		// Create PDO object
		$this->dbConnect();
		// Query.
		$this->res = $this->pdo->query("SELECT content_id, content_name
						FROM tbl_contents
						WHERE content_parent=0 AND content_hide_in_top_links=0");
	}

	// Get sub-link SQL.
	public function getSubLinkSQL($c)
	{
		// If arg sent.
		if(isset($c))
		{
			// Create PDO object
			$this->dbConnect();
			// Build prepared statement.
			if(($stmt = $this->pdo->prepare("SELECT content_id, content_name
							 FROM tbl_contents
							 WHERE content_parent=:c AND content_hide_in_top_links=0")))
			{
				// Execute.
				if($stmt->execute(array(':c' => $c)))
				{
					// Loop.
					$this->resB = $stmt;
				}
			}
		}
	}

	// Get footer SQL.
	public function getFooterSQL()
	{
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
	public function getHomepageXSQL($lr)
	{
		// Create PDO object
		$this->dbConnect();
		// Query.
		$this->res = $this->pdo->query("SELECT content_id, content_name, content_details
						FROM tbl_contents
						WHERE content_inc_on_homepage_".$lr."x=1
						ORDER BY content_id");
	}

	// Check if content has sub-links
	public function checkForSubLinks($c)
	{
		// Init.
		$ToF = FALSE;
		// If arg sent.
		if(isset($c))
		{
			// Create PDO object
			$this->dbConnect();
			// Build prepared statement.
			$stmt = $this->pdo->prepare("SELECT content_id
						     FROM tbl_contents
						     WHERE content_parent=:c AND content_parent<>1 AND content_hide_in_top_links=0
						     LIMIT 1");
			// Execute.
			if($stmt->execute(array(':c' => $c)))
			{
				// Loop.
				while($stmt->fetch())
				{
					// Set.
					$ToF = TRUE;
				}
			}
		}
		// Return.
		return $ToF;
	}

	// Check if this is the content section currently being used.
	public function checkIfSectionSel($c,$p)
	{
	 	// Init.
	 	$sel = FALSE;
		// If args are passed.
		if(isset($c) && isset($p))
		{
			// Create PDO object
			$this->dbConnect();
			// If the content is already the parent.
			if($c == $p)
			{
				// Set.
				$sel = TRUE;
			}
			// Otherwise, if not at root.
			elseif($c != 0 && $c != 99999 && $sel == FALSE)
			{
				// Build prepared statement.
				if(($stmt = $this->pdo->prepare("SELECT content_parent
								 FROM tbl_contents
								 WHERE content_id=:c
								 LIMIT 1")))
				{
					if($stmt->execute(array(':c' => $c)))
					{
						// Bind by column name.
						$stmt->bindColumn('content_parent', $content_parent);
						// Loop.
//$stmt->fetch(PDO::FETCH_BOUND)
						while($stmt->fetch())
						{
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
	public function checkContentExists($c)
	{
		// Init.
		$ToF = FALSE;
		// If arg sent.
		if(isset($c))
		{
			// Create PDO object
			$this->dbConnect();
			// Build prepared statement.
			if(($stmt = $this->pdo->prepare("SELECT content_id
							 FROM tbl_contents
							 WHERE content_id=:c
							 LIMIT 1")))
			{
				// Execute.
				if($stmt->execute(array(':c' => $c)))
				{
					// Loop.
					while($stmt->fetch())
					{
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
	public function getContentDetails($c)
	{
		// If arg sent.
		if(isset($c) && $this->checkContentExists($c))
		{
			// Create PDO object
			$this->dbConnect();
			// Build prepared statement.
			if(($stmt = $this->pdo->prepare("SELECT content_id, content_name, content_details
							 FROM tbl_contents
							 WHERE content_id=:c")))
			{
				// Execute.
				if($stmt->execute(array(':c' => $c)))
				{
					// Loop.
					$this->res = $stmt;
				}
			}
		}
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
							 WHERE value_group_fk=:g")))
			{
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

}

?>
