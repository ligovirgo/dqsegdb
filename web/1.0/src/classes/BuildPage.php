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
require_once('DAO.php');
require_once('GetStructure.php');
require_once('InitVar.php');

// Page builder class.
class BuildPage
{

	private $document;
 
	public function __construct()
	{
		// Instantiate.
		$dao = new DAO();
		$variable = new Variables();
		// Set content call ID.
		$variable->getContentCallID();
		// If on homepage.
		if($variable->c == 1) {
			// If the default host has not been set.
			if(!isset($_SESSION['default_host']) || empty($_SESSION['default_host'])) {
				// Set default host.
				$_SESSION['default_host'] = $dao->get_default_host();
			}
		}
		// Instantiate.
		$structure = new GetStructure();
		// Get header.
		$structure->getHeader();
		// Get header.
		$structure->getBody();
		// Get footer.
		$structure->getFooter();
		// Build document.
		$this->document = $structure->hdr;
		$this->document .= $structure->bdy;
		$this->document .= $structure->ftr;
		echo $this->document;
	}
}

?>
