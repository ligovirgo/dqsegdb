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
            $this->visualisation_contents .= "<p><strong><i class=\"fas fa-link\"></i> <a href=\"?c=1\" class=\"link\">Get some more segments</a>\n";
            $this->visualisation_contents .= "<div id=\"div_view_segments\" class=\"w3-margin-right w3-padding-0\">\n";
            $this->visualisation_contents .= "<p id=\"p_view_segments\"><i class=\"fas fa-spinner w3-spin\"></i> Building segment visualisation...</p>\n";
            $this->visualisation_contents .= "</div>\n";
        }
    }
    
}

?>