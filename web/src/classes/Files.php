<?php

// Get libraries.
require_once('DAO.php');
require_once('InitVar.php');

// File-handling class.
class Files {

	/* Make a JSON file. */
	public function make_json_file($in_file, $data) {
		// Init.
		$r = FALSE;
		// Instantiate.
		$dao = new DAO();
		$variable = new Variables();
		// Get file-related variables.
		$variable->get_file_related_variables();
		// If put to file successful.
		if(file_put_contents($variable->doc_root.$variable->download_dir.$in_file, $data)) {
			// Insert file metadata to database.
			if($dao->insert_file_metadata($in_file, 'json')) {
				// Set.
				$r = TRUE;
			}
		}
		// Return.
		return $r;
	}

	/* Make a non-JSON file. */
	public function make_non_json_file($in_file, $out_file, $data, $format) {
		// If the format being requested is not JSON.
		if($format != 'json') {
			// Instantiate.
			$dao = new DAO();
			$variable = new Variables();
			// Get file-related variables.
			$variable->get_file_related_variables();
			// Convert file to different format, too.
			shell_exec($variable->doc_root.$variable->python_utilities_dir.'convert_formats.py '.$variable->doc_root.$variable->download_dir.$in_file." -o ".$variable->doc_root.$variable->download_dir.$out_file." -t ".$format);
			// Insert file metadata to database.
			$dao->insert_file_metadata($out_file, $format);
		}
	}
}

?>
