<?php

// Get libraries.
require_once('GetLogFile.php');

// Page structure class.
class GetStructure {
	public $hdr;
	public $bdy;
	public $ftr;

	public $div;
	public $tab_str;
	public $brk;
	
	private $str;

	// Get header.
	public function get_header() {
 	 	// Set hdr.
		$this->hdr = "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">";
		$this->hdr .= "<html xmlns=\"http://www.w3.org/1999/xhtml\">\n\n";
		// Open head.
		$this->hdr .= "<head>\n\n";
		$this->hdr .= "	<!-- Link to stylesheets. -->\n";
//		$this->hdr .= "	<link href=\"css/general.css\" rel=\"stylesheet\" type=\"text/css\" />\n";
		$this->hdr .= "	<!-- Website icon. -->\n";
//		$this->hdr .= "	<link rel=\"shortcut icon\" href=\"images/dqsegdb_wui.ico\" />\n";
		$this->hdr .= "	<!-- Output meta data. -->\n";
		$this->hdr .= "	<meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\" />\n";
		$this->hdr .= "	<!-- Disable robots. -->\n";
		$this->hdr .= "	<meta name=\"robots\" content=\"noindex,nofollow,noarchive\" />\n";
		$this->hdr .= "	<meta name=\"googlebot\" content=\"noindex,nofollow,noarchive\" />\n";
		$this->hdr .= "	<meta name=\"slurp\" content=\"noindex,nofollow,noarchive\" />\n";
		$this->hdr .= "	<meta name=\"msnbot\" content=\"noindex,nofollow,noarchive\" />\n";
		$this->hdr .= "	<meta name=\"teoma\" content=\"noindex,nofollow,noarchive\" />\n";
		$this->hdr .= "	<!-- Output title. -->\n";
		$this->hdr .= "	<title>DQSEGDB - Log File Analysis Tool</title>\n";
		$this->hdr .= "	<!-- Call Javascripts. -->\n";
//		$this->hdr .= "	<script type=\"text/javascript\" src=\"scripts/custom.js\"></script>\n";
		// Close head.
		$this->hdr .= "</head>\n\n";
		// Open body.
		$this->hdr .= "<body>\n\n";
	}

	// Get body.
	public function get_body() {
		// Instantiate.
		$logfile = new GetLogFile();
		// Get log file analysis.
		$this->bdy .= $logfile->get_log_file_analysis(2);
	}

	// Get footer.
	public function get_footer() {
		// Close body.
		$this->ftr .= "</body>\n\n";
		$this->ftr .= "</html>";
	}
	

	// Get required tabs.
	public function get_required_tabs($tabs) {
		// Init.
		$this->tab_str = NULL;
		// Add number of tabs required.
		for($a=0;$a<$tabs;$a++) {
			$this->tab_str .= "	";
		}
	}

	// Get a break.
	public function get_break($tabs) {
		// Add number of tabs required.
	 	$this->get_required_tabs($tabs);
	 	// Build break.
		$this->brk = $this->tab_str."<!-- Output break div. -->\n";
		$this->brk = $this->tab_str."<div class=\"break\"></div>\n\n";
	}

	// Open div.
	public function open_div($name,$tabs,$class,$js) {
	 	// Set class.
	 	if(isset($class)) {
			$class = " class=\"$class\"";
		}
		// If JavaScript is set.
		if(isset($js)) {
			$js = " ".$js;
		}
		// Add number of tabs required.
	 	$this->get_required_tabs($tabs);
		// Set comment.
		$this->div = $this->tab_str."<!--- Output $name div -->\n";
		// Open div.
		$this->div .= $this->tab_str."<div id=\"div_$name\"$class$js>\n\n";
	}

	// Close div.
	public function close_div($name,$tabs) {
		// Add break.
	 	$this->get_break($tabs+1);
		$this->div = $this->brk;
		// Add number of tabs required.
	 	$this->get_required_tabs($tabs);
		// Set comment.
		$this->div .= $this->tab_str."<!--- Close $name div -->\n";
		// Close div.
		$this->div .= $this->tab_str."</div>\n\n";
	}

}

?>