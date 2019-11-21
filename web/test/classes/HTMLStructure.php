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
require_once 'Constants.php';
require_once 'DAO.php';
require_once 'Logger.php';

// Page structure class.
class HTMLStructure {

    public $header;
    public $footer;
    
    public $nav_bars;
    public $shell;
	
	public $right_hand_options;
	public $warning_modal;
	public $info_modal;
	public $left_slidenav;
	
	private $links;
	
	/* Build the navigation bars. */
	public function build_nav_bars() {
		// Init.
		$this->nav_bars = NULL;
		// Build links for large screens.
		$this->nav_bars .= "	<!-- Navbar on large screens -->\n";
		$this->nav_bars .= "	<div class=\"w3-top\">\n";
		$this->nav_bars .= "		<ul class=\"w3-navbar w3-theme-vigilanza w3-left-align w3-large\">\n";
		$this->nav_bars .= "			<li class=\"w3-hide-large w3-opennav w3-right\">\n";
		$this->nav_bars .= "				<a class=\"w3-hover-white w3-large w3-theme-vim\" href=\"javascript:void(0);\" onclick=\"openNav()\"><i class=\"fas fa-bars\"></i></a>\n";
		$this->nav_bars .= "			</li>\n";
		$this->nav_bars .= "			<li><a href=\"?c=1\" class=\"w3-dark-grey\"><i class=\"fas fa-home w3-margin-right\"></i> DQSEGDB</a></li>\n";
		$this->nav_bars .= "		</ul>\n";
		$this->nav_bars .= "	</div>\n";
		// Build links for small screens.
		$this->nav_bars .= "	<!-- Navbar on small screens -->\n";
		$this->nav_bars .= "	<div id=\"navDemo\" class=\"w3-hide w3-hide-large w3-top\" style=\"margin-top:43px;\">\n";
		$this->nav_bars .= "		<ul class=\"w3-navbar w3-left-align w3-large w3-theme\">\n";
		$this->nav_bars .= "		</ul>\n";
		$this->nav_bars .= "	</div>\n";
	}
	
	/* Build the right-hand options. */
	public function build_right_hand_options() {
		// Init.
		$this->right_hand_options = NULL;
		// Build.
		$this->right_hand_options .= "	<!-- Get right-hand options container -->\n";
		$this->right_hand_options .= "	<div class=\"w3-container\" style=\"top:50px;\">\n";
		// Output Line buttons.
		//$this->right_hand_options .= "		<a href=\"?c=2\" class=\"dashboard-btn w3-signal-green w3-tooltip\" style=\"top:78px\"><i class=\"fas fa-user\"><span style=\"left:-52px\" class=\"w3-text w3-tag w3-signal-green w3-animate-right text-tip\">Members</span></i></a>\n";
		//$this->right_hand_options .= "		<a href=\"?c=3\" class=\"dashboard-btn w3-signal-green w3-tooltip\" style=\"top:106px\"><i class=\"fas fa-university\"><span style=\"left:-70px\" class=\"w3-text w3-tag w3-signal-green w3-animate-right text-tip\">Institutions</span></i></a>\n";
		$this->right_hand_options .= "	</div>\n";
	}

	/* Build the generic warning modal. */
	public function build_warning_modal() {
		// Init.
		$this->warning_modal = NULL;
		// Build.
		$this->warning_modal .= "	<!--  Set generic warning modal -->\n";
		$this->warning_modal .= "	<div id=\"warning-modal\" class=\"w3-modal\">\n";
		$this->warning_modal .= "		<div class=\"w3-modal-content w3-animate-top w3-card-8\">\n";
		$this->warning_modal .= "			<header class=\"w3-container w3-red\">\n";
		$this->warning_modal .= "				<span onclick=\"close_warning_modal()\" class=\"w3-closebtn\">&times;</span>\n";
		$this->warning_modal .= "	        		<h2>Warning</h2>\n";
		$this->warning_modal .= "			</header>\n";
		$this->warning_modal .= "			<div class=\"w3-container\">\n";
		$this->warning_modal .= "				<p id=\"p-warning\"></p>\n";
		$this->warning_modal .= "			</div>\n";
		$this->warning_modal .= "		</div>\n";
		$this->warning_modal .= "	</div>\n";
	}

	/* Build the info modal. */
	public function build_info_modal() {
	    // Init.
	    $this->info_modal = NULL;
	    // Build.
	    $this->info_modal .= "	<!--  Set info modal -->\n";
	    $this->info_modal .= "	<div id=\"info-modal\" class=\"w3-modal\">\n";
	    $this->info_modal .= "		<div class=\"w3-modal-content w3-animate-top w3-card-8\">\n";
	    $this->info_modal .= "			<header class=\"w3-container w3-signal-green\">\n";
	    $this->info_modal .= "				<span onclick=\"close_info_modal()\" class=\"w3-closebtn\">&times;</span>\n";
	    $this->info_modal .= "	        		<h2><i class=\"far fa-question-circle\"></i> Info</h2>\n";
	    $this->info_modal .= "			</header>\n";
	    $this->info_modal .= "			<div class=\"w3-container\">\n";
	    $this->info_modal .= "				<h4 id=\"hdr-info\" style=\"font-weight:bold\"></h4>\n";
	    $this->info_modal .= "				<div id=\"div-info-contents\"></div>\n";
	    $this->info_modal .= "			</div>\n";
	    $this->info_modal .= "		</div>\n";
	    $this->info_modal .= "	</div>\n";
	}
	
	/* Build the header. */
	public function build_header() {
	    // Init.
	    $this->header = NULL;
	    // Build.
	    $this->header .= "<!DOCTYPE html>\n";
	    $this->header .= "<html lang=\"en\">\n";
	    $this->header .= "<title>DQSEGDB</title>\n";
	    $this->header .= "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n";
	    $this->header .= "<meta charset=\"utf-8\">\n";
	    $this->header .= "<meta http-equiv=\"Cache-Control\" content=\"no-store\" />\n";
	    $this->header .= "<link rel=\"shortcut icon\" href=\"resources/dqsegdb.ico?1\">\n";
	    $this->header .= "<link rel=\"stylesheet\" href=\"css/dqsegdb.css\">\n";
	    $this->header .= "<link rel=\"stylesheet\" href=\"css/jquery-ui.css\">\n";
	    $this->header .= "<link rel=\"stylesheet\" href=\"css/fontawesome-free-5.5.0-web/css/all.css\">\n";
	    $this->header .= "<script type=\"text/javascript\" src=\"scripts/jquery/jquery-1.12.4.js\"></script>\n";
	    $this->header .= "<script type=\"text/javascript\" src=\"scripts/jquery/jquery-ui-1.12.1.js\"></script>\n";
	    $this->header .= "<script type=\"text/javascript\" src=\"scripts/dqsegdb.js\"></script>\n";
	    $this->header .= "<script type=\"text/javascript\" src=\"scripts/timepicker.js\"></script>\n";
	    $this->header .= "<script type=\"text/javascript\" src=\"scripts/zingchart/zingchart.min.js\"></script>\n";
	    $this->header .= "<body id=\"body_noemi\">\n";
	}
	
	/* Build the footer. */
	public function build_footer() {
	    // Init.
	    $this->footer = NULL;
	    // Build.
	    $this->footer .= "	<!--  Close off the page -->\n";
	    $this->footer .= "	<body>\n";
	    $this->footer .= "</html>\n";
	}
}

?>