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