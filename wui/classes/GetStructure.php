<?php

// Get libraries.
require_once('DAO.php');
require_once('GetContent.php');
require_once('InitVar.php');

// Page structure class.
class GetStructure
{
	public $hdr;
	public $bdy;
	public $ftr;
	public $div;

	public $tabStr;
	public $brk;
	public $rowspacer;

	private $current_host_div;
	private $str;
	private $menuCall;
	private $searchBox;

	// Get header.
	public function getHeader() {
 	 	// Set hdr.
		$this->hdr = "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">";
		$this->hdr .= "<html xmlns=\"http://www.w3.org/1999/xhtml\">\n\n";
		// Open head.
		$this->hdr .= "<head>\n\n";
		$this->hdr .= "	<!-- Link to stylesheets. -->\n";
		$this->hdr .= "	<link href=\"css/general.css\" rel=\"stylesheet\" type=\"text/css\" />\n";
		$this->hdr .= "	<!-- Website icon. -->\n";
		$this->hdr .= "	<link rel=\"shortcut icon\" href=\"images/dqsegdb_wui.ico\" />\n";
		$this->hdr .= "	<!-- Output meta data. -->\n";
		$this->hdr .= "	<meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\" />\n";
		$this->hdr .= "	<!-- Disable robots. -->\n";
		$this->hdr .= "	<meta name=\"robots\" content=\"noindex,nofollow,noarchive\" />\n";
		$this->hdr .= "	<meta name=\"googlebot\" content=\"noindex,nofollow,noarchive\" />\n";
		$this->hdr .= "	<meta name=\"slurp\" content=\"noindex,nofollow,noarchive\" />\n";
		$this->hdr .= "	<meta name=\"msnbot\" content=\"noindex,nofollow,noarchive\" />\n";
		$this->hdr .= "	<meta name=\"teoma\" content=\"noindex,nofollow,noarchive\" />\n";
		$this->hdr .= "	<!-- Output title. -->\n";
		$this->hdr .= "	<title>DQSEGDB - Data Quality Segment DataBase - Web Interface</title>\n";
		$this->hdr .= "	<!-- Call Javascripts. -->\n";
		$this->hdr .= "	<script type=\"text/javascript\" src=\"scripts/custom.js\"></script>\n";
		$this->hdr .= "	<script type=\"text/javascript\" src=\"scripts/jquery/jquery-1.7.1.js\"></script>\n";
		$this->hdr .= "	<script type=\"text/javascript\" src=\"scripts/jquery/jquery.easing.1.3.js\"></script>\n";
		$this->hdr .= "	<script type=\"text/javascript\" src=\"scripts/jquery/jquery.hoverIntent.minified.js\"></script>\n";
		$this->hdr .= "	<script type=\"text/javascript\" src=\"scripts/jquery/jquery.naviDropDown.1.0.js\"></script>\n";
		$this->hdr .= "	<script type=\"text/javascript\" src=\"scripts/d3/d3.v3.js\" charset=\"utf-8\"></script>\n";
		// Get menu call.
		$this->getMenuCall();
		$this->hdr .= $this->menuCall;
		// Close head.
		$this->hdr .= "</head>\n\n";
		// Open body.
		$this->hdr .= "<body>\n\n";
	}

	// Get body.
	public function getBody() {
		// Instantiate.
		$content = new GetContent();
		// Open main structure divs.
		$this->openDiv('shell',1,'');
		$this->bdy = $this->div;
		$this->openDiv('main',2,'');
		// Open upper div.
		$this->bdy .= $this->div;
		$this->openDiv('upper',3,'');
		$this->bdy .= $this->div;
		// Upper content - Search bar.
		$this->openDiv('search_bar',4,'');
		$this->bdy .= $this->div;
		// Get Current host box.
		$this->get_current_host_div(4);
		$this->bdy .= $this->current_host_div;
		// Get Search.
//		$this->getSearchBox(5);
//		$this->bdy .= $this->searchBox;
		$this->closeDiv('search_bar',4);
		$this->bdy .= $this->div;
		// Upper content - Upper left.
		$this->openDiv('upper_lx',4,'');
		$this->bdy .= $this->div;
		// Get header text image.
		$this->bdy .= "					<img src=\"images/dqsegdb_hdr_txt.png\" alt=\"\" id=\"img_hdr_txt\" />\n";
		$this->closeDiv('upper_lx',4);
		$this->bdy .= $this->div;
		// Upper content - Upper right.
		$this->openDiv('upper_rx',4,'');
		$this->bdy .= $this->div;
		// Get logo image.
		$this->bdy .= "					<img src=\"images/logo.png\" alt=\"\" id=\"img_logo\" />\n";
		$this->closeDiv('upper_rx',4);
		$this->bdy .= $this->div;
		$this->bdy .= "";
		// Close upper div.
		$this->closeDiv('upper',3);
		$this->bdy .= $this->div;
		// Get top links.
		$this->getTopLinks(3);
		$this->bdy .= $this->str;
		// Get content.
		$content->buildContent(4);
		$this->bdy .= $content->contents;
	}

	// Get footer.
	public function getFooter() {
		// Open footer div.
		$this->openDiv('footer',3,'');
		$this->ftr .= $this->div;
		// Get footer links.
		$dao = new DAO();
		$dao->getFooterSQL();
		$res = $dao->res;
		// Bind by column name.
		$res->bindColumn('content_id', $content_id);
		$res->bindColumn('content_name', $content_name);
		// Loop.
		while($res->fetch()) {
			// Build.
			$this->ftr .= "<a href=\"?c=".$content_id."\" class=\"footer_link\">".strtoupper($content_name)."</a>\n\n";
		}
		// Close footer div.
		$this->closeDiv('footer',3);
		$this->ftr .= $this->div;
		// Close main div.
		$this->closeDiv('main',2);
		$this->ftr .= $this->div;
		// Open footer base left div.
		$this->openDiv('footer_base_lx',2,'');
		$this->ftr .= $this->div;
		// Close footer base left div.
		$this->closeDiv('footer_base_lx',2);
		$this->ftr .= $this->div;
		// Open footer base div.
		$this->openDiv('footer_base',2,'');
		$this->ftr .= $this->div;
		// Close footer base div.
		$this->closeDiv('footer_base',2);
		$this->ftr .= $this->div;
		// Open footer base right div.
		$this->openDiv('footer_base_rx',2,'');
		$this->ftr .= $this->div;
		// Close footer base right div.
		$this->closeDiv('footer_base_rx',2);
		$this->ftr .= $this->div;
		// Close shell div.
		$this->closeDiv('shell',1);
		$this->ftr .= $this->div;
		// Close body.
		$this->ftr .= "</body>\n\n";
		$this->ftr .= "</html>";
	}

	// Get required tabs.
	public function getRequiredTabs($tabs) {
		// Init.
		$this->tabStr = NULL;
		// Add number of tabs required.
		for($a=0;$a<$tabs;$a++)
		{
			$this->tabStr .= "	";
		}
	}

	// Get a break.
	public function getBreak($tabs) {
		// Add number of tabs required.
	 	$this->getRequiredTabs($tabs);
	 	// Build break.
		$this->brk = $this->tabStr."<!-- Output break div. -->\n";
		$this->brk = $this->tabStr."<div class=\"break\"></div>\n\n";
	}

	// Open div.
	public function openDiv($name,$tabs,$class) {
	 	// Set class.
	 	if($class != NULL) {
			$class = " class=\"$class\"";
		}
		// Add number of tabs required.
	 	$this->getRequiredTabs($tabs);
		// Set comment.
		$this->div = $this->tabStr."<!--- Output $name div -->\n";
		// Open div.
		$this->div .= $this->tabStr."<div id=\"div_$name\"$class>\n\n";
	}

	// Close div.
	public function closeDiv($name,$tabs)
	{
		// Add break.
	 	$this->getBreak($tabs+1);
		$this->div = $this->brk;
		// Add number of tabs required.
	 	$this->getRequiredTabs($tabs);
		// Set comment.
		$this->div .= $this->tabStr."<!--- Close $name div -->\n";
		// Close div.
		$this->div .= $this->tabStr."</div>\n\n";
	}

	// Get a rounded content div.
	public function getRoundedContentDiv($name,$title,$content,$tabs)
	{
		// Add number of tabs required.
	 	$this->getRequiredTabs($tabs);
		// Set.
		$this->div = $this->tabStr."<!-- Output $name rounded content div. -->\n";
		$this->div .= $this->tabStr."<!-- Output title. -->\n";
		$this->div .= $this->tabStr."<div class=\"t\"><div class=\"b\"><div class=\"rHdr\"><div class=\"l\">\n";
		$this->div .= $this->tabStr."	<div class=\"blHdr\"><div class=\"brHdr\"><div class=\"tl\"><div id=\"div_title_$name\" class=\"tr\">\n";
		$this->div .= $this->tabStr."		$title\n";
		$this->div .= $this->tabStr."	</div></div></div></div>\n";
		$this->div .= $this->tabStr."</div></div></div></div>\n\n";
		$this->div .= $this->tabStr."<!-- Output content. -->\n";
		$this->div .= $this->tabStr."<div class=\"tCon\"><div class=\"bCon\"><div class=\"r\"><div class=\"l\">\n";
		$this->div .= $this->tabStr."	<div class=\"bl\"><div class=\"br\"><div class=\"tlCon\"><div id=\"div_contents_$name\" class=\"trCon\">\n\n";
		$this->div .= $this->tabStr."$content\n\n";
		$this->div .= $this->tabStr."	<!-- Close $name rounded content div. -->\n";
		$this->div .= $this->tabStr."	</div></div></div></div>\n";
		$this->div .= $this->tabStr."</div></div></div></div>\n\n";
	}
	
	// Get a light-blue div.
	function getFlatLightBlueDiv($name,$title,$content,$img,$bg,$tabs)
	{
		// Add number of tabs required.
	 	$this->getRequiredTabs($tabs);
		// Set.
		$this->div = $this->tabStr."<!-- Output $name box div. -->\n\n";
		$wTitle = NULL;
		if($title != NULL)
		{
			$wTitle = "_w_title";
		}
		$this->div .= $this->tabStr."<div id=\"hdr_$name\" class=\"flat_light_blue_hdr$wTitle\">\n\n";
		$this->div .= $this->tabStr."	<div id=\"tl_$name\" class=\"flat_light_blue".$bg."_tl\"></div>\n\n";
		if($title != NULL)
		{
			$this->div .= $this->tabStr."	<div id=\"".$name."_title\" class=\"flat_light_blue_title\">\n\n";
			$this->div .= $this->tabStr."		<p>$title</p>\n\n";
			$this->div .= $this->tabStr."	</div>\n\n";
		}
		$this->div .= $this->tabStr."	<div id=\"tr_$name\" class=\"flat_light_blue".$bg."_tr\"></div>\n\n";
		$this->div .= $this->tabStr."</div>\n\n";
		$this->div .= $this->tabStr."<div id=\"$name\" class=\"flat_light_blue_bg\">\n\n";
		$this->div .= $this->tabStr."	<div id=\"".$name."_content\" class=\"flat_light_blue_content\">\n\n";
		$this->div .= $this->tabStr."		$content\n\n";
		$this->div .= $this->tabStr."	</div>\n\n";
		$this->div .= $this->tabStr."</div>\n\n";
		$this->div .= $this->tabStr."<div id=\"ftr_$name\" class=\"flat_light_blue_ftr\">\n\n";
		$this->div .= $this->tabStr."	<div id=\"bl_$name\" class=\"flat_light_blue".$bg."_bl\"></div>\n\n";
		$this->div .= $this->tabStr."	<div id=\"br_$name\" class=\"flat_light_blue".$bg."_br\"></div>\n\n";
		$this->div .= $this->tabStr."</div>\n\n";
		$this->div .= $this->tabStr."<!-- Close $name box div. -->\n\n";
		// Add break.
	 	$this->getBreak($tabs+1);
		$this->div .= $this->brk;
	}

	// Get an azzure div.
	function getAzzureDiv($name,$title,$content,$img,$tabs)
	{
		// Add number of tabs required.
	 	$this->getRequiredTabs($tabs);
		// Set.
		$this->div = $this->tabStr."<!-- Output $name box div. -->\n\n";
		$this->div .= $this->tabStr."<div id=\"hdr_$name\" class=\"azzure_hdr\">\n\n";
		$this->div .= $this->tabStr."	<div id=\"tl_$name\" class=\"azzure_tl\"></div>\n\n";
		$this->div .= $this->tabStr."	<div id=\"".$name."_title\" class=\"azzure_title\">\n\n";
		$this->div .= $this->tabStr."		<p>$title</p>\n\n";
		$this->div .= $this->tabStr."	</div>\n\n";
		$this->div .= $this->tabStr."	<div id=\"tr_$name\" class=\"azzure_tr\"></div>\n\n";
		$this->div .= $this->tabStr."</div>\n\n";
		$this->div .= $this->tabStr."<div id=\"$name\" class=\"azzure_bg\">\n\n";
		$this->div .= $this->tabStr."	<div id=\"".$name."_content\" class=\"azzure_content\">\n\n";
		$this->div .= $this->tabStr."		$content\n\n";
		$this->div .= $this->tabStr."	</div>\n\n";
		$this->div .= $this->tabStr."</div>\n\n";
		$this->div .= $this->tabStr."<div id=\"ftr_$name\" class=\"azzure_ftr\">\n\n";
		$this->div .= $this->tabStr."	<div id=\"bl_$name\" class=\"azzure_bl\"></div>\n\n";
		$this->div .= $this->tabStr."	<div id=\"br_$name\" class=\"azzure_br\"></div>\n\n";
		$this->div .= $this->tabStr."</div>\n\n";
		$this->div .= $this->tabStr."<!-- Close $name box div. -->\n\n";
		// Add break.
	 	$this->getBreak($tabs+1);
		$this->div .= $this->brk;
	}

	// Get a grey div.
	function getGreyDiv($name,$title,$content,$img,$tabs)
	{
		// Add number of tabs required.
	 	$this->getRequiredTabs($tabs);
		// Set.
		$this->div = $this->tabStr."<!-- Output $name box div. -->\n\n";
		$this->div .= $this->tabStr."<div id=\"hdr_$name\" class=\"grey_hdr\">\n\n";
		$this->div .= $this->tabStr."	<div id=\"tl_$name\" class=\"grey_tl\"></div>\n\n";
		$this->div .= $this->tabStr."	<div id=\"".$name."_title\" class=\"grey_title\">\n\n";
		$this->div .= $this->tabStr."		<p>$title</p>\n\n";
		$this->div .= $this->tabStr."	</div>\n\n";
		$this->div .= $this->tabStr."	<div id=\"tr_$name\" class=\"grey_tr\"></div>\n\n";
		$this->div .= $this->tabStr."</div>\n\n";
		$this->div .= $this->tabStr."<div id=\"$name\" class=\"grey_bg\">\n\n";
		$this->div .= $this->tabStr."	<div id=\"".$name."_content\" class=\"grey_content\">\n\n";
		$this->div .= $this->tabStr."		$content\n\n";
		$this->div .= $this->tabStr."	</div>\n\n";
		$this->div .= $this->tabStr."</div>\n\n";
		$this->div .= $this->tabStr."<div id=\"ftr_$name\" class=\"grey_ftr\">\n\n";
		$this->div .= $this->tabStr."	<div id=\"bl_$name\" class=\"grey_bl\"></div>\n\n";
		$this->div .= $this->tabStr."	<div id=\"br_$name\" class=\"grey_br\"></div>\n\n";
		$this->div .= $this->tabStr."</div>\n\n";
		$this->div .= $this->tabStr."<!-- Close $name box div. -->\n\n";
		// Add break.
	 	$this->getBreak($tabs+1);
		$this->div .= $this->brk;
	}

	// Get row spacer.
	public function getRowSpacer($tabs)
	{
		// Open cover div.
		$this->rowspacer = $this->openDiv('div_cov',$tabs+1,'coverDiv');
		// Close cover div.
		$this->rowspacer .= $this->closeDiv('div_cov',$tabs+1);
	}

	// Get top_links.
	private function getTopLinks($tabs) {
		// Initiate.
		$dao = new DAO();
		$variable = new Variables();
		// Init.
		$this->str = NULL;
		$variable->getContentCallID();
		$c = $variable->c;
		// Add number of tabs required.
	 	$this->getRequiredTabs($tabs);
		// Open top links.
		$this->str .= $this->tabStr."<div class=\"top_links_container\">\n";
		$this->str .= $this->tabStr."	<div id=\"navigation_horiz\">\n";
		$this->str .= $this->tabStr."   	 	<ul>\n";
		// Get contents from DB for links.
		$sql = $dao->getTopLinkSQL();
		$res = $dao->res;
		// Loop.
		while($loop = $res->fetch()) {
			// Set.
			$content_id = $loop["content_id"];
			$content_name = strtoupper($loop["content_name"]);
			$content_uri = $loop["content_uri"];
			$arrow = NULL;
			// If this content has sub-links.
			if($dao->checkForSubLinks($content_id)) {
				// Display down arrow.
				$arrow = "&nbsp;<img id=\"img_sub_link_arrow_".$content_id."\" src=\"images/sub_link_arrow.png\" alt=\"\" title=\"\" class=\"sub_link_arrow\" />";
			}
			// Check if this is the content section currently being used.
			$s = NULL;
			if($dao->checkIfSectionSel($c,$content_id)) {
				$s = "_sel";
			}
			// If content has an alternative URI.
			if(!empty($content_uri)) {
				$uri = $content_uri;
			}
			else {
				$uri = "?c=".$content_id;
			}
			// Build link.
			$this->str .= $this->tabStr."			<li>\n";
			$this->str .= $this->tabStr."				<a href=\"".$uri."\" class=\"navlink".$s."\">".$content_name.$arrow."</a>\n";
			// If this content has sub-links.
			if($dao->checkForSubLinks($content_id)) {
				// Build drop-down.
				$this->str .= $this->tabStr."				<div class=\"dropdown\" id=\"dropdown_box_".$content_id."\">\n";      
				// Get sub-links.
				$dao->getSubLinkSQL($content_id);
				$resB = $dao->resB;
				// Bind by column name.
				$resB->bindColumn('content_id', $cid);
				$resB->bindColumn('content_name', $content_name);
				$resB->bindColumn('content_uri', $c_uri);
				// Loop.
				while($resB->fetch()) {
					// Set.
					$name = strtoupper($content_name);
					// Check if this is the content section currently being used.
					$sl = NULL;
					if($dao->checkIfSectionSel($c,$cid))
					{
						$sl = "_sel";
					}
					// If content has an alternative URI.
					if(!empty($c_uri)) {
						$l_uri = $c_uri;
					}
					else {
						$l_uri = "?c=".$cid;
					}
					// Build.
					$this->str .= $this->tabStr."					<a href=\"".$l_uri."\" class=\"sub_link".$sl."\">".$name."</a>\n";
				}
				// End drop-down.
				$this->str .= $this->tabStr."				</div><!-- .dropdown_menu -->\n";
			}
			$this->str .= $this->tabStr."			</li>\n";
		}
		// Get end of container.
		$this->str .= $this->tabStr."		</ul>\n";
		$this->str .= $this->tabStr."	</div>\n";
		$this->str .= $this->tabStr."</div>\n";
	}

	// Get the menu.
	private function getMenuCall()
	{
		// Init.
		$this->menuCall = "	<script type=\"text/javascript\">\n";
		$this->menuCall .= "	$(function(){\n";
		$this->menuCall .= "		$('#navigation_horiz').naviDropDown({\n";
		$this->menuCall .= "			dropDownWidth: '300px'\n";
		$this->menuCall .= "		});\n";
		$this->menuCall .= "		$('#navigation_vert').naviDropDown({\n";
		$this->menuCall .= "			dropDownWidth: '300px',\n";
		$this->menuCall .= "			orientation: 'vertical'\n";
		$this->menuCall .= "		});\n";
		$this->menuCall .= "	});\n";
		$this->menuCall .= "	</script>\n";
	}

	// Get search box.
	private function getSearchBox($tabs)
	{
		// Add number of tabs required.
	 	$this->getRequiredTabs($tabs);
		// Open form.
		$this->searchBox .= $this->tabStr."<form id=\"frm_search\" name=\"frm_search\" method=\"post\" action=\"?c=28\">\n\n";
		// Get search box.
		$this->searchBox .= $this->tabStr."	<input id=\"search_txt\" name=\"search_txt\" type=\"text\" value=\"Search...\" onclick=\"clearInputBox(this)\" />\n\n";
		// Get search img.
		$this->searchBox .= $this->tabStr."	<input id=\"search_glass\" type=\"image\" src=\"images/search_glass.png\" />\n\n";
		// Close form.
		$this->searchBox .= $this->tabStr."</form>\n\n";
	}

	// Get current host div.
	private function get_current_host_div($tabs) {
		// Instantiate.
		$dao = new DAO();
		$variable = new Variables();
		// Set content call ID.
		$variable->getContentCallID();
		// If on homepage.
		if($variable->c == 1) {
			// Open.
			$this->openDiv('current_host',$tabs,'');
			$this->current_host_div = $this->div;
			// Get current-host div contents.
			$this->current_host_div .= $this->get_current_host_div_contents($tabs);
			// Close.
			$this->closeDiv('current_host',$tabs);
			$this->current_host_div .= $this->div;
			// Open.
			$this->openDiv('change_host',$tabs,'');
			$this->current_host_div .= $this->div;
			$this->current_host_div .= "<span id=\"span_change_host\" class=\"span_change_host\" onclick=\"activate_host_change_option()\">Change this host</span>";
			// Close.
			$this->closeDiv('change_host',$tabs);
			$this->current_host_div .= $this->div;
		}
	}

	// Get current-host div contents.
	public function get_current_host_div_contents($tabs) {
		// Init.
		$r = NULL;
		// Instantiate.
		$dao = new DAO();
		// If changing host.
		if(isset($_SESSION['changing_current_host']) && $_SESSION['changing_current_host']) {
			// Add number of tabs required.
		 	$this->getRequiredTabs($tabs);
			// Open select.
			$r .= $this->tabStr."<select id=\"sel_change_host\" name=\"sel_change_host\" onchange=\"update_host()\">\n";
			// Get array of hosts.
			$a = $dao->get_value_array(2);
			// Loop array.
			foreach($a as $id => $host) {
				// Get additional text available for this host.
				$add_info = $dao->get_value_add_info($host);
				// If passed.
				if(isset($add_info)) {
					// Set.
					$add_info = " (".$add_info." data)";
				}
				// Set selected.
				$sel = NULL;
				// If host is current default host.
				if($host == $_SESSION['default_host']) {
					// Set selected option.
					$sel = " selected=\"selected\"";
				}
				// Set option.
				$r .= $this->tabStr."	<option value=\"".$host."\"".$sel.">".$host.$add_info."</option>\n";
			}
			// Close select.
			$r .= $this->tabStr."</select>\n";
		}
		// Otherwise, if not changing host.
		else {
			// Get additional text available for this host.
			$add_info = $dao->get_value_add_info($_SESSION['default_host']);
			// If additional information available.
			if(isset($add_info)) {
				// Set.
				$add_info = " (".$add_info." data)";
			}
			// Set.
			$r .= "Currently using: <span class=\"uri_like\">".$_SESSION['default_host'].$add_info."</span>";
		}
		// Return.
		return $r;
	}
	
	// Output a form type structure.
	function get_form_structure($f, $i, $t) {
		// If explanatory text sent.
		if(isset($t)) {
			// Add required style.
			$t = "<br />\n<span class=\"span_frm_info\">(".$t.")</span>\n";
		}
	 	// Set.
		$r = "<div class=\"div_row_cover\">\n".
			   "	<div class=\"div_row_hdr\" id=\"input_".$f."_hdr\">".$f.$t."</div>\n".
			   "	<div class=\"div_row_details\" id=\"input_".$f."_val\">".$i."</div>\n".
			   "</div>\n";
		// Return.
		return $r;
	}

	// Get a button.
	function get_button($id, $txt, $form, $way, $direction, $callJS, $tabs, $txtClass) {
		// Init.
		$str = NULL;
		// Add number of tabs required.
		$this->getRequiredTabs($tabs);
		// Handle direction order.
	 	$defDir = "Left";
	 	if($direction != NULL) {
			$defDir = $direction;
		}
		// Decide which Javascript to use.
		if($callJS != NULL) {
			$js = $callJS;
		}
		// Otherwise, set to redirect.
		else {
			$js = "redirect('$form','$way')";
		}
		// Incorporate Javascript in onclick.
		$js = "onclick=\"$js\"";
		// Set the button.
		$str .= $this->tabStr."<!-- Open $txt button. -->\n";
		$str .= $this->tabStr."<div id=\"divFor$id\" class=\"buttonContainer$defDir$txtClass\" $js>\n";
		$str .= $this->tabStr."	<!-- Output button arrow. -->\n";
		$str .= $this->tabStr."	<img id=\"imgFor$id\" src=\"images/button_lx.png\" class=\"buttonLeft\" alt=\"\" />\n";
		$str .= $this->tabStr."	<!-- Output button text. -->\n";
		$str .= $this->tabStr."	<div id=\"$id\" class=\"buttonRight\">".strtoupper($txt)."</div>\n";
		$str .= $this->tabStr."<!-- Close $txt button. -->\n";
		$str .= $this->tabStr."</div>\n\n";
		// Return.
		return $str;
	}
}

?>
