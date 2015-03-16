<?php

// Start sessions.
session_start();

// Set error display level.
ini_set('display_errors',0);
ini_set('memory_limit', '-1');

// Set default timezone.
date_default_timezone_set("UTC");

// Set max execution time.
set_time_limit(7200);

// Get libraries.
require_once('classes/BuildPage.php');

// Build page.
$worker = new BuildPage();

?>