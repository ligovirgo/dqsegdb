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
DQSEGDB - Convert segdb-format data to DQSEGDB.
*/

// Time conversions.
class TimeConversion {
	
	// Convert Unix Time to GPS Time
	public function unix2gps($unixTime) {
		// Add offset in seconds
		if (fmod($unixTime, 1) != 0) {
			$unixTime = $unixTime - 0.5;
			$isLeap = 1;
		} else {
			$isLeap = 0;
		}
		$gpsTime = $unixTime - 315964800;
		$nleaps = $this->countleaps($gpsTime, 'unix2gps');
		$gpsTime = $gpsTime + $nleaps + $isLeap;
		return $gpsTime;
	}
	
	// Define GPS leap seconds
	private function getleaps() {
		$leaps = array(46828800, 78364801, 109900802, 173059203, 252028804, 315187205, 346723206, 393984007, 425520008, 457056009, 504489610, 551750411, 599184012, 820108813, 914803214, 1025136015);
		return $leaps;
	}
	
	// Test to see if a GPS second is a leap second
	private function isleap($gpsTime) {
		$isLeap = FALSE;
		$leaps = $this->getleaps();
		$lenLeaps = count($leaps);
		for ($i = 0; $i < $lenLeaps; $i++) {
			if ($gpsTime == $leaps[$i]) {
				$isLeap = TRUE;
			}
		}
		return $isLeap;
	}
	
	// Count number of leap seconds that have passed
	private function countleaps($gpsTime, $dirFlag) {
		$leaps = $this->getleaps();
		$lenLeaps = count($leaps);
		$nleaps = 0;  // number of leap seconds prior to gpsTime
		for ($i = 0; $i < $lenLeaps; $i++) {
			if (!strcmp('unix2gps', $dirFlag)) {
				if ($gpsTime >= $leaps[$i] - $i) {
					$nleaps++;
				}
			} elseif (!strcmp('gps2unix', $dirFlag)) {
				if ($gpsTime >= $leaps[$i]) {
					$nleaps++;
				}
			} else {
				echo "ERROR Invalid Flag!";
			}
		}
		return $nleaps;
	}
	
	// Convert GPS Time to Unix Time
	public function gps2unix($gpsTime) {
		// Add offset in seconds
		$unixTime = $gpsTime + 315964800;
		$nleaps = $this->countleaps($gpsTime, 'gps2unix');
		$unixTime = $unixTime - $nleaps;
		if ($this->isleap($gpsTime)) {
			$unixTime = $unixTime + 0.5;
		}
		return $unixTime;
	}
	
	// Convert bespoke segdb insertion times to MySQL-readable format.
	public function convert_bespoke_segdb_datetimes($d) {
		// Init.
		$r = NULL;
		// If arg passed.
		if(isset($d)) {
			// Get individual components.
			$dmy = substr($d, 0, 10);
			$h = substr($d, 11, 2);
			$m = substr($d, 14, 2);
			$s = substr($d, 17, 2);
			// Set.
			$r = $dmy.' '.$h.':'.$m.':'.$s;
		}
		// Return.
		return $r;
	}
	
}

?>