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

// Get libraries.
require_once 'DAO.php';

class User {
	
    /* Get the normalised ID for the currently-authenticated user. */
    public function get_valid_user_id() {
        // Init.
        $r = 0;
        // If the username is set.
        if(isset($_SERVER['eduPersonPrincipalName']) && !empty($_SERVER['eduPersonPrincipalName'])) {
            // Instantiate.
            $dao = new DAO();
            // Get the ID for this user.
            $r = $dao->get_user_id($_SERVER['eduPersonPrincipalName']);
            // If no user found.
            if($r == 0) {
                // Insert user to database.
                if($dao->insert_user($_SERVER['eduPersonPrincipalName'])) {
                    // Attempt again to get the ID for this user.
                    $r = $dao->get_user_id($_SERVER['eduPersonPrincipalName']);
                }
            }
        }
        // Return.
        return $r;
    }
    
}

?>