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
/*
This file is part of the DQSEGDB WUI.

This file was written by Gary Hemming <gary.hemming@ego-gw.it>.

DMS-WUI uses the following open source software:
- jQuery JavaScript Library v1.12.4, available under the MIT licence - http://jquery.org/license - Copyright jQuery Foundation and other contributors.
- W3.CSS 2.79 by Jan Egil and Borge Refsnes.
- Font Awesome by Dave Gandy - http://fontawesome.io.
*/

require_once 'DAO.php';
require_once 'Logger.php';

class Visualisation {
    
    public $visualisation_contents;
    
    /* Build the visualisation contents. */
    public function build_visualisation_contents() {
        // Init.
        $this->visualisation_contents = NULL;
        // If on the correct page.
        if($_GET['c'] == 2) {
            $this->visualisation_contents .= "<h3 class=\"w3-text-signal-green\">View segments</h3>\n";
            $this->visualisation_contents .= "<p><i class=\"fas fa-link\"></i> <a href=\"?c=1\" class=\"link\">Get some more segments</a>\n";
            $this->visualisation_contents .= "<div id=\"div_view_segments\" class=\"w3-margin-right w3-padding-0\">\n";
            $this->visualisation_contents .= "<p id=\"p_view_segments\"><i class=\"fas fa-spinner w3-spin\"></i> Building segment visualisation...</p>\n";
            $this->visualisation_contents .= "</div>\n";
        }
    }
    
}

?>