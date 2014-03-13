<?php

// Get libraries.
require_once('DAO.php');
require_once('GetServerData.php');
require_once('GetStructure.php');

// Page content class.
class GetContent
{
	public $contents;
	
	private $page;
	private $log_file_info;

	// Get content.
	public function buildContent($tabs)
	{
		// Initiate.
		$dao = new DAO();
		$structure = new GetStructure();
		$variable = new Variables();
		// Init.
		$variable->getContentCallID();
		$c = $variable->c;
		$this->contents = NULL;
 	 	// Check that content actually exists in the database.
 	 	if($dao->checkContentExists($c))
		{
			// Get contents.
			if($c == 1)
			{
				// Get homepage.
				$this->getHomepage($tabs);
			}
			else
			{
				// Get sub-page.
				$this->getSubpage($c,$tabs);
			}
			// Set.
			$this->contents .= $this->page;
		}
	}

	// Get homepage.
	function getHomepage($tabs)
	{
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
		while($res->fetch())
		{
			// Set.
			$i++;
			$content_name = strtoupper($content_name);
			if($i == 2)
			{
				// Get all resources.
				$serverdata->get_current_server_status($content_id);
				// Get enclosed display div.
				$structure->getFlatLightBlueDiv('lx_'.$content_id,$content_name,$content_details.$serverdata->server_status,NULL,"_on_white",$tabs+2);
				$this->page .= $structure->div;
				$i = 0;
			}
			else
			{
				// Get enclosed display div.
				$structure->getAzzureDiv('lx_'.$content_id,$content_name,$content_details.$serverdata->get_query_form_div($tabs+2),NULL,$tabs+2);
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
		while($res->fetch())
		{
			// Get enclosed display div.
			$structure->getFlatLightBlueDiv('lx_'.$content_id,$content_name,$content_details,NULL,NULL,$tabs+3);
			$rxStr .= $structure->div;
		}
		// Open About us div.
		$structure->getGreyDiv("recent_activity","Recent activity",$rxStr,NULL,$tabs+2);
		$this->page .= $structure->div;
		// Close middle-right div.
		$structure->closeDiv('middle_right',$tabs);
		$this->page .= $structure->div;
		// Close middle div.
		$structure->closeDiv('middle',$tabs);
		$this->page .= $structure->div;
	}

	// Get sub-page.
	function getSubpage($c,$tabs)
	{
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
		while($res->fetch())
		{
			// Add server log files.
			$this->get_server_log_files($content_id, $tabs);
			$content_details .= $this->log_file_info;
			// Get enclosed display div.
			$structure->getFlatLightBlueDiv('div_content_'.$content_id,$content_name,$content_details,NULL,"_on_white",$tabs+1);
		}
		$this->page .= $structure->div;
		// Close middle div.
		$structure->closeDiv('middle',$tabs);
		$this->page .= $structure->div;
	}

	// Get server log files.
	function get_server_log_files($c,$tabs) {
		// If in the correct area.
		if($c == 29) {
			// Init.
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
						$this->log_file_info .= "<p><strong>".$max_events." most recently logged events (".$f."):</strong></p>\n";
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
						$this->log_file_info .= "<code>".substr($events, 0, -7)."</code>\n";
						$this->log_file_info .= "<p><strong>Most recent log files:</strong></p>\n";
						// If not viewing an individual file.
						if(!$get_f) {
							$this->log_file_info .= "<p>Click on a filename to view the contents.</p>\n";
						}
						else {
							$this->log_file_info .= "<p><a href=\"?c=".$c."\">Stop viewing file contents</a></p>\n";
						}
					}
				}
			}
			// Incorporate in code tag.
			$this->log_file_info .= "<code>".substr($log_files, 0, -7)."</code>\n";
		}
	}

}

?>
