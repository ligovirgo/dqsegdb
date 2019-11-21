<?php
/*
 This file is part of the DQSEGDB WUI.
 
 This file was written by Gary Hemming <gary.hemming@ego-gw.it>.
 
 DQSEGDB WUI uses the following open source software:
 - jQuery JavaScript Library v1.12.4, available under the MIT licence - http://jquery.org/license - Copyright jQuery Foundation and other contributors.
 - W3.CSS by Jan Egil and Borge Refsnes.
 - Font Awesome by Dave Gandy - http://fontawesome.io.
 - Jquery Timepicker, developed and maintained by Willington Vega. Code licensed under the MIT and GPL licenses - http://timepicker.co
 */

// Get libraries.
require_once('Constants.php');
require_once('DAO.php');

// File-handling class.
class Files {
    
    public $file_details;

	/* Make a JSON file. */
	public function make_json_file($in_file, $data) {
		// Init.
		$r = FALSE;
		// Instantiate.
		$constants = new Constants();
		$dao = new DAO();
		// Get file-related variables.
		$constants->get_file_constants();
		// If put to file successful.
		if(file_put_contents($constants->doc_root.$constants->download_dir.$in_file, $data)) {
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
		    $constants = new Constants();
		    $dao = new DAO();
			// Get file-related variables.
		    $constants->get_file_constants();
			// Convert file to different format, too.
		    shell_exec($constants->doc_root.$constants->python_utilities_dir.'convert_formats.py '.$constants->doc_root.$constants->download_dir.$in_file." -o ".$constants->doc_root.$constants->download_dir.$out_file." -t ".$format);
			// Insert file metadata to database.
			$dao->insert_file_metadata($out_file, $format);
		}
	}
	
	/* Build an output payload. */
	public function build_output_payload($data, $f) {
	    // Init.
	    $r = NULL;
	    // Instantiate.
	    $constants = new Constants();
	    $dao = new DAO();
	    // Get file-related variables.
	    $constants->get_file_constants();
    	// If JSON passed.
    	if(!empty($data)) {
    	    // Get UNIX timestamp.
    	    $unix_ts = time();
    	    // Set in-file filename.
    	    $in_file = $unix_ts.'.json';
    	    // Make JSON file.
    	    if($this->make_json_file($in_file, $data)) {
    	        // Set out-file filename.
    	        $out_file = $unix_ts.'.'.$f;
    	        // Make non-JSON file.
    	        $this->make_non_json_file($in_file, $out_file, $data, $f);
    	        // Set file to open automatically, replacing underscre with point, so as to enable JSON data to to be formatted in browser.
    	        $r = $constants->download_dir.$unix_ts.'.'.str_replace('_', '.', $f);
    	        // Return the ID of the file that has just been inserted.
    	        //$r = $dao->get_new_file_id($in_file);
    	    }
    	}
    	// Return ID.
    	return $r;
	}
	
	/* Get the details for the most-recent file produced by a specific user. */
	public function get_latest_file_details() {
	    // Instantiate.
	    $dao = new DAO();
	    $id = $dao->get_new_file_id();
        $this->get_file_details($id);
        return $id;
	}

	/* Get details of a file. */
	public function get_file_details($f) {
	    // Init.
	    $this->file_details;
	    // Instantiate.
	    $constants = new Constants();
	    $dao = new DAO();
	    // Get file details array.
	    $a = $dao->get_file_details($f);
	    // Get file-related variables.
	    $constants->get_file_constants();
	    // Build the output full path.
	    $img_file_name = str_replace('.json', '.png', $a[0]['file_name']);
	    $ofp = $constants->doc_root.$constants->plots_dir.$img_file_name;
	    // Generate the PNG from the JSON.
	    shell_exec($constants->doc_root.$constants->python_utilities_dir.'generate_plots.py '.$constants->doc_root.$constants->download_dir.$a[0]['file_name']." -o ".$ofp);
	    // Output the file plot.
	    $this->file_details .= "<img src=\"".$constants->plots_dir.$img_file_name."\">\n";
	    $this->file_details .= "<p><strong>File:</strong> <a href=\"".$constants->download_dir.$a[0]['file_name']."\" class=\"link\">".$a[0]['file_name']."</a> (".$a[0]['file_size']." Bytes)<br>\n";
	    $this->file_details .= "<strong>URI used:</strong> ".$a[0]['file_uri_used']."</p>\n";
	    $this->file_details .= "<div id=\"div_raw_json\" class=\"w3-container w3-border w3-responsive\" style=\"height:200px\"><i class=\"fas fa-spinner w3-spin\"></i> Getting JSON payload...</div>\n";
	}

	/* Get the latest JSON payload produced by a specific user. */
	public function get_latest_json_payload() {
	    // Instantiate.
	    $dao = new DAO();
	    $constants = new Constants();
	    // File constants.
	    $constants->get_file_constants();
	    // Get and return the contents of the JSON file.
	    $id = $dao->get_new_file_id();
	    $a = $dao->get_file_details($id);
	    return json_encode($constants->download_dir.file_get_contents($a[0]['file_name']));
	}
	
}

?>
