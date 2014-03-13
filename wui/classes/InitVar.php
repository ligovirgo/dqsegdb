<?php

// Set error reporting.
ini_set("display_errors","1");

// Initialise variables.
class Variables
{
	public $host;
	public $db;
	public $db_user;
	public $db_pass;

	public $server_host;

	public $ad_type;
	public $c;

	public function initVariables()
	{
		// DB & server connection variables.
		$this->host = "localhost";
		$this->db = "dqsegdb_wui";
		$this->db_user = "dqsegdb_wui_user";
		$this->db_pass = "dqsegdb_wui_pw";
	}
	
	// Get admin type.
	public function getAdminType()
	{
		if(isset($_GET["ad_type"]))
		{
			$this->ad_type = $_GET["ad_type"];
		}
	}

	// Get content call ID.
	public function getContentCallID()
	{
		if(isset($_GET["c"]))
		{
			$this->c = $_GET["c"];
		}
		else
		{
			$this->c = 1;
		}
	}

}

?>