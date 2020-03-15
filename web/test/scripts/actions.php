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

DQSEGDB WUI uses the following open source software:
- jQuery JavaScript Library v1.12.4, available under the MIT licence - http://jquery.org/license - Copyright jQuery Foundation and other contributors.
- W3.CSS 2.75 by Jan Egil and Borge Refsnes.
- Font Awesome by Dave Gandy - http://fontawesome.io.
- Jquery Timepicker, developed and maintained by Willington Vega. Code licensed under the MIT and GPL licenses - http://timepicker.co
*/

// Start PHP up and initialise everything required.
require_once('../init/initialise.php');

// Get libraries.
require_once('../classes/JSActions.php');

// Build page.
$worker = new JSAction();

// If redirect required.
if(isset($_GET['redirect'])) {
    $args = NULL;
    // Return to sent content.
    if(isset($_GET['c'])) {
        $args .= '&c='.$_GET['c'];
    }
    if(isset($_GET['m'])) {
        $args .= '&m='.$_GET['m'];
    }
    if(isset($_GET['i'])) {
        $args .= '&i='.$_GET['i'];
    }
    if(isset($_GET['g'])) {
        $args .= '&g='.$_GET['g'];
    }
    if(!empty($args)) {
        $args = '?'.substr($args, 1);
    }
    // Redirect.
	header('location: ../'.$args);
}

?>