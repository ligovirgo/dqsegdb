<?php

/////////////////////////////////////
// DQSEGDB log file analysis tool //
///////////////////////////////////

// Start sessions.
session_start();

// Set error display level.
ini_set('display_errors', 0);
//ini_set('memory_limit', '-1');

// Get libraries.
require_once('classes/BuildPage.php');

// Build page.
$worker = new BuildPage();

?>