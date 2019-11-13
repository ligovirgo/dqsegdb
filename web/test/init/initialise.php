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

// Start sessions.
session_start();

// Set error display level.
ini_set('display_errors', 0);

// Set default timezone.
date_default_timezone_set('Europe/Rome');

// Set content area by default.
if(!isset($_GET['c'])) {
    $_GET['c'] = 1;
}

?>