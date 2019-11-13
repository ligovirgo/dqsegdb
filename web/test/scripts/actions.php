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