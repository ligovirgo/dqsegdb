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

// Utility class.
class Utils {
	
	/* Create a randomly generated string. */
	public function get_random_string($len) {
		// Init.
		$str = NULL;
		// Get alphabetical array.
		$alphas = array_merge(range('A','Z'),range('a','z'));
		// Loop through and build random directory of 8 chars.
		for($a=0;$a<$len;$a++)	{
			// If numeric.
		 	if(rand(1,2) == 1) {
		  		$str .= rand(0,9);
			}
			// If alphabetic.
			else {
		  		$rand_keys = array_rand($alphas,2);
		  		$str .= $alphas[$rand_keys[0]];
		 	}
	 	}
		// Return random str.
		return $str;
	}
	
	/* Strip all attributes from HTML tags. */
	public function strip_html_tag_attributes($t) {
		// Strip tags.
		$r = preg_replace('/(<[^>]+) style=".*?"/i', '$1', $t);
		// Ensure links follow the required style.
		$r = str_replace('<a ', '<a class="blue-link" ', $r);
		// Return.
		return $r;
	}

	/* Convert a user entered dd-mm-yyyy date to MySQL date format. */
	public function convert_date_to_mysql($d) {
		// Create from format.
		$converted_date = DateTime::createFromFormat('d-m-Y', $d);
		$new_date = date_format($converted_date, 'Y-m-d');
		// Return.
		return $new_date;
		
	}
	
	/* Convert seconds to days, hours, minutes and seconds. */
	public function seconds_to_time($s) {
		// Set.
		$dtf = new \DateTime('@0');
		$dtt = new \DateTime("@".$s);
		// Return.
		return $dtf->diff($dtt)->format('%ad %hh %im %ss');
	}
	
	/* Convert GPS time UTC. */
	public function gps_to_utc($gps) {
	    // Subtract UTC seconds and add GPS leap seconds.
	    $utc = $gps + 315964764 + 19;
		// Return.
		return $utc;
	}
	
	/* Convert accented characters to LaTEK. */
	public function convert_accents_to_latek($s) {
	    // Init.
	    $a = array();
	    // Build the array.
	    $a["à"] = '\`a';
        $a["è"] = '\`e';
        $a["ì"] = '\`\i';
        $a["ò"] = '\`o';
        $a["ù"] = '\`u';
        $a["ỳ"] = '\`y';
        $a["À"] = '\`A';
        $a["È"] = '\`E';
        $a["Ì"] = '\`\I';
        $a["Ò"] = '\`O';
        $a["Ù"] = '\`U';
        $a["Ỳ"] = '\`Y';
        $a["á"] = '\'a';
        $a["é"] = '\'e';
        $a["í"] = '\'\i';
        $a["ó"] = '\'o';
        $a["ú"] = '\'u';
        $a["ý"] = '\'y';
        $a["Á"] = '\'A';
        $a["É"] = '\'E';
        $a["Í"] = '\'\I';
        $a["Ó"] = '\'O';
        $a["Ú"] = '\'U';
        $a["Ý"] = '\'Y';
        $a["â"] = '\^a';
        $a["ê"] = '\^e';
        $a["î"] = '\^\i';
        $a["ô"] = '\^o';
        $a["û"] = '\^u';
        $a["ŷ"] = '\^y';
        $a["Â"] = '\^A';
        $a["Ê"] = '\^E';
        $a["Î"] = '\^\\I';
        $a["Ô"] = '\^O';
        $a["Û"] = '\^U';
        $a["Ŷ"] = '\^Y';
        $a["ä"] = '\\"a';
        $a["ë"] = '\\"e';
        $a["ï"] = '\\"\i';
        $a["ö"] = '\\"o';
        $a["ü"] = '\\"u';
        $a["ÿ"] = '\\"y';
        $a["Ä"] = '\\"A';
        $a["Ë"] = '\\"E';
        $a["Ï"] = '\\"\I';
        $a["Ö"] = '\\"O';
        $a["Ü"] = '\\"U';
        $a["Ÿ"] = '\\"Y';
        $a["ç"] = '\c{c}';
        $a["Ç"] = '\c{C}';
        $a["œ"] = '{\oe}';
        $a["Œ"] = '{\OE}';
        $a["æ"] = '{\ae}';
        $a["Æ"] = '{\AE}';
        $a["å"] = '{\aa}';
        $a["Å"] = '{\AA}';
        $a["ø"] = '{\o}';
        $a["Ø"] = '{\O}';
        $a["ß"] = '{\ss}';
        $a["ñ"] = '\~n';
        // Loop through the LaTEX array.
        foreach($a as $k => $v) {
            // Replace any of the characters found in the passed string.
            $s = str_replace($k, $v, $s);
        }
        // Return amended string.
        return $s;
	}
}

?>