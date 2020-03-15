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

// Get libraries.
require_once 'Constants.php';
require_once 'Logger.php';
require_once 'TimeConversion.php';

// Data Access Object class.
class DAO {
	
	public $pdo;
	public $body;

	/////////////////////////
	// GENERAL CONNECTION //
	///////////////////////

	// Connect to database.
	public function db_connect() {
		// Create new variables object.
		$constant = new Constants();
		$constant->db_connection_constants();
		// If connection not made.
		if(!$this->pdo || !$this->pdo) {
			// Create new PDO object for DQSEGDB.
			$this->pdo = new PDO("mysql:host=".$constant->host.";dbname=".$constant->db, $constant->db_user, $constant->db_pass);
			// Create new PDO object for DQSEGDB.
//			$this->pdo = new PDO("mysql:host=".$constant->host.";dbname=".$constant->db_segdb, $constant->db_user, $constant->db_pass);
		}
	}

	/////////////////////
	// UPDATE RELATED //
	///////////////////

	// Run conversion.
	public function run_conversion() {
		// Init.
		$this->body = NULL;
		// Instantiate.
		$constant = new Constants();
		$log = new Logger();
		// Get version constant.
		$constant->package_version_constants();
		// Log.
		$log->write_to_log("Starting DQSEGDB Automatic Converter (version: ".$constant->package_version.")");
		// Create segdb DB.
		if(!$this->create_segdb_db()) {
			// Log.
			$log->write_to_log("1. ERROR - Unable to successfully create segdb schema.");
		}
		else {
			// Log.
			$log->write_to_log("1. segdb schema successfully created.");
			// Import segdb CSV data.
			if(!$this->import_segdb_csv_data()) {
				// Log.
				$log->write_to_log("2. ERROR - Unable to successfully import segdb CSV data.");
			}
			else {
				// Log.
				$log->write_to_log("2. segdb CSV data successfully imported.");
				// Create DQSEGDB DB.
				if(!$this->create_dqsegdb_db()) {
					// Log.
					$log->write_to_log("3. ERROR - Unable to successfully create DQSEGDB schema.");
				}
				else {
					// Log.
					$log->write_to_log("3. DQSEGDB schema successfully created.");
					// Insert segdb ifo to DQSEGDB.
					if(!$this->insert_segdb_ifo_to_dqsegdb()) {
						// Log.
						$log->write_to_log("4. ERROR - Unable to successfully convert ifos to DQSEGDB format.");
					}
					else {
						// Log.
						$log->write_to_log("4. Ifos conversion completed.");
						// Insert segdb users to DQSEGDB.
						if(!$this->insert_segdb_users_to_dqsegdb()) {
							// Log.
							$log->write_to_log("5. ERROR - Unable to successfully convert users to DQSEGDB format.");
						} 
						else {
							// Log.
							$log->write_to_log("5. User conversion completed.");
							// Convert segment definers to flags.
							if(!$this->convert_segment_definers_to_flags()) {
								// Log.
								$log->write_to_log("6. ERROR - Unable to successfully convert segment definers to flags.");
							}
							else {
								// Log.
								$log->write_to_log("6. Segment definers successfully converted to flags.");
								// Convert segment definers to versions.
								if(!$this->convert_segment_definers_to_versions()) {
									// Log.
									$log->write_to_log("7. ERROR - Unable to successfully convert segment definers to versions.");
								}
								else {
									// Log.
									$log->write_to_log("7. Segment definers successfully converted to versions.");
									// Associate versions.
									if(!$this->associate_versions()) {
										// Log.
										$log->write_to_log("8. ERROR - Unable to successfully associate versions to associated-version field in flag table.");
									}
									else {
										// Log.
										$log->write_to_log("8. Versions successfully associated to flags in flag table.");
										// Convert segments.
										if(!$this->convert_segments(FALSE)) {
											// Log.
											$log->write_to_log("9. ERROR - Unable to successfully convert segments from segdb to DQSEGDB format.");
										}
										else {
											// Log.
											$log->write_to_log("9. Segments successfully converted from segdb to DQSEGDB format.");
											// Convert segment summaries.
											if(!$this->convert_segments(TRUE)) {
												// Log.
												$log->write_to_log("10. ERROR - Unable to successfully convert segment summaries from segdb to DQSEGDB format.");
											}
											else {
												// Log.
												$log->write_to_log("10. Segment summaries successfully converted from segdb to DQSEGDB format.");
												// Check, analyse and optimise each of the tables.
												if(!$this->db_optimisation()) {
													// Log.
													$log->write_to_log("11. ERROR - Check, analysis and optimisation of the DB not completed successfully.");
												}
												else {
													// Log.
													$log->write_to_log("11. Check, analysis and optimisation of the DB completed successfully.");
													// Update version URI.
													if(!$this->update_version_uri()) {
														// Log.
														$log->write_to_log("11.b ERROR - Unable to successfully update version URI.");
													}
													else {
														// Log.
														$log->write_to_log("11.b Version URI updated successfully.");
														// Update known version-segment totals.
														if(!$this->update_version_segment_totals(FALSE)) {
															// Log.
															$log->write_to_log("12. ERROR - Unable to successfully update known version-segment totals.");
														}
														else {
															// Log.
															$log->write_to_log("12. Known version-segment totals updated successfully.");
															// Update active version-segment totals.
															if(!$this->update_version_segment_totals(TRUE)) {
																// Log.
																$log->write_to_log("13. ERROR - Unable to successfully update active version-segment totals.");
															}
															else {
																// Log.
																$log->write_to_log("13. Active version-segment totals updated successfully.");
																// Update known earliest version-segment boundaries.
																if(!$this->update_version_segment_boundaries(FALSE, FALSE)) {
																	// Log.
																	$log->write_to_log("14. ERROR - Unable to successfully update known earliest version-segment boundaries.");
																}
																else {
																	// Log.
																	$log->write_to_log("14. Known earliest version-segment boundaries updated successfully.");
																	// Update known latest version-segment boundaries.
																	if(!$this->update_version_segment_boundaries(FALSE, TRUE)) {
																		// Log.
																		$log->write_to_log("15. ERROR - Unable to successfully update known latest version-segment boundaries.");
																	}
																	else {
																		// Log.
																		$log->write_to_log("15. Known latest version-segment boundaries updated successfully.");
																		// Update active earliest version-segment boundaries.
																		if(!$this->update_version_segment_boundaries(TRUE, FALSE)) {
																			// Log.
																			$log->write_to_log("16. ERROR - Unable to successfully update active earliest version-segment boundaries.");
																		}
																		else {
																			// Log.
																			$log->write_to_log("16. Active earliest version-segment boundaries updated successfully.");
																			// Update active latest version-segment boundaries.
																			if(!$this->update_version_segment_boundaries(TRUE, TRUE)) {
																				// Log.
																				$log->write_to_log("17. ERROR - Unable to successfully update active latest version-segment boundaries.");
																			}
																			else {
																				// Log.
																				$log->write_to_log("17. Active latest version-segment boundaries updated successfully.");
																				// Convert processes.
																				if(!$this->convert_processes()) {
																					// Log.
																					$log->write_to_log("18. ERROR - Unable to successfully convert processes.");
																				}
																				else {
																					// Log.
																					$log->write_to_log("18. Processes converted successfully.");
																					// Update version comments.
																					if(!$this->update_version_comments()) {
																						// Log.
																						$log->write_to_log("18.b ERROR - Unable to successfully update version comments.");
																					}
																					else {
																						// Log.
																						$log->write_to_log("18.b Version comments updated successfully.");
																						// Coalesce processes.
																						if(!$this->coalesce_processes()) {
																							// Log.
																							$log->write_to_log("19. ERROR - Unable to successfully coalesce processes.");
																						}
																						else {
																							// Log.
																							$log->write_to_log("19. Processes successfully coalesced.");
																							// Associate process args.
																							if(!$this->associate_process_args()) {
																								// Log.
																								$log->write_to_log("20. ERROR - Unable to successfully associate process args.");
																							}
																							else {
																								// Log.
																								$log->write_to_log("20. Process args associated successfully.");
																								// Update known start process-segment boundaries.
																								if(!$this->update_process_segment_boundaries(FALSE, FALSE)) {
																									// Log.
																									$log->write_to_log("21. ERROR - Unable to successfully update process known-segment start boundaries.");
																								}
																								else {
																									// Log.
																									$log->write_to_log("21. Process known-segment start boundaries updated successfully.");
																									// Update known end process-segment boundaries.
																									if(!$this->update_process_segment_boundaries(FALSE, TRUE)) {
																										// Log.
																										$log->write_to_log("22. ERROR - Unable to successfully update process known-segment end boundaries.");
																									}
																									else {
																										// Log.
																										$log->write_to_log("22. Process known-segment end boundaries updated successfully.");
																										// Update active start process-segment boundaries.
																										if(!$this->update_process_segment_boundaries(TRUE, FALSE)) {
																											// Log.
																											$log->write_to_log("23. ERROR - Unable to successfully update process active-segment start boundaries.");
																										}
																										else {
																											// Log.
																											$log->write_to_log("23. Process active-segment start boundaries updated successfully.");
																											// Update active process-segment end boundaries.
																											if(!$this->update_process_segment_boundaries(TRUE, TRUE)) {
																												// Log.
																												$log->write_to_log("24. ERROR - Unable to successfully update process active-segment end boundaries.");
																											}
																											else {
																												// Log.
																												$log->write_to_log("24. Process active-segment end boundaries updated successfully.");
																												// Update active process-segment totals.
																												if(!$this->update_process_segment_totals(TRUE)) {
																													// Log.
																													$log->write_to_log("25. ERROR - Unable to successfully update process-segment active totals.");
																												}
																												else {
																													// Log.
																													$log->write_to_log("25. Process-segment active totals updated successfully.");
																													// Update known process-segment totals.
																													if(!$this->update_process_segment_totals(FALSE)) {
																														// Log.
																														$log->write_to_log("26. ERROR - Unable to successfully update process-segment known totals.");
																													}
																													else {
																														// Log.
																														$log->write_to_log("26. Process-segment known totals updated successfully.");
																														// Re-alter schema.
																														if(!$this->re_alter_schema()) {
																															// Log.
																															$log->write_to_log("27. ERROR - Unable to re-alter DQSEGDB schema, removing segdb fields used in conversion.");
																														}
																														else {
																															// Log.
																															$log->write_to_log("27. DQSEGDB schema altered, segdb fields used in conversion removed.");
																															// Check, analyse and optimise each of the tables.
																															if(!$this->db_optimisation()) {
																																// Log.
																																$log->write_to_log("28. ERROR - Check, analysis and optimisation of the DB not completed successfully.");
																															}
																															else {
																																// Log.
																																$log->write_to_log("28. Check, analysis and optimisation of the DB completed successfully.");
																																// Log.
																																$log->write_to_log("segdb >>> DQSEGDB conversion process now complete.");
																															}
																														}
																													}
																												}
																											}
																										}
																									}
																								}
																							}
																						}
																					}
																				}
																			}
																		}
																	}
																}
															}
														}
													}
												}
											}
										}
									}
								}
							}
						}
					}
				}
			}
		}
		// Log.
		$log->write_to_log("DQSEGDB Automatic Converter (version: ".$constant->package_version.") stopped.");
	}
	
	// Create segdb DB.
	private function create_segdb_db() {
		// Init.
		$r = FALSE;
		// Create PDO object
		$this->db_connect();
		// Alter DB structure.
		if($this->pdo->query("CREATE TABLE IF NOT EXISTS `PROCESS` (
									  `PROGRAM` varchar(128) NOT NULL,
									  `VERSION` varchar(64) NOT NULL,
									  `CVS_REPOSITORY` varchar(256) NOT NULL,
									  `CVS_ENTRY_TIME` char(12) NOT NULL,
									  `COMMENT` varchar(255) NOT NULL,
									  `IS_ONLINE` int(4) NOT NULL,
									  `NODE` varchar(64) NOT NULL,
									  `USERNAME` char(64) NOT NULL,
									  `UNIX_PROCID` int(4) NOT NULL,
									  `START_TIME` int(4) NOT NULL,
									  `END_TIME` char(12) NOT NULL,
									  `JOBID` int(4) NOT NULL,
									  `DOMAIN` varchar(255) NOT NULL,
									  `PROCESS_ID` char(26) NOT NULL,
									  `PARAM_SET` char(4) NOT NULL,
									  `IFOS` char(12) NOT NULL,
									  `INSERTION_TIME` varchar(52) NOT NULL
									) ENGINE=InnoDB DEFAULT CHARSET=latin1;
									CREATE TABLE IF NOT EXISTS `PROCESS_PARAMS` (
									  `PROGRAM` varchar(128) NOT NULL,
									  `PROCESS_ID` char(26) NOT NULL,
									  `PARAM` varchar(32) NOT NULL,
									  `TYPE` varchar(16) NOT NULL,
									  `VALUE` varchar(1024) NOT NULL,
									  `INSERTION_TIME` varchar(26) NOT NULL
									) ENGINE=InnoDB DEFAULT CHARSET=latin1;
									CREATE TABLE IF NOT EXISTS `SEGMENT` (
									  `PROCESS_ID` char(26) NOT NULL,
									  `SEGMENT_ID` char(26) NOT NULL,
									  `START_TIME` int(12) NOT NULL,
									  `END_TIME` int(12) NOT NULL,
									  `INSERTION_TIME` varchar(26) NOT NULL,
									  `SEGMENT_DEF_ID` char(26) NOT NULL
									) ENGINE=InnoDB DEFAULT CHARSET=latin1;
									CREATE TABLE IF NOT EXISTS `SEGMENT_DEFINER` (
									  `PROCESS_ID` char(26) NOT NULL,
									  `SEGMENT_DEF_ID` char(26) NOT NULL,
									  `IFOS` char(12) NOT NULL,
									  `NAME` varchar(128) NOT NULL,
									  `VERSION` int(4) NOT NULL,
									  `COMMENT` varchar(255) NOT NULL,
									  `INSERTION_TIME` varchar(26) NOT NULL
									) ENGINE=InnoDB DEFAULT CHARSET=latin1;
									CREATE TABLE IF NOT EXISTS `SEGMENT_SUMMARY` (
									  `SEGMENT_SUM_ID` char(26) NOT NULL,
									  `START_TIME` int(12) NOT NULL,
									  `END_TIME` int(12) NOT NULL,
									  `COMMENT` varchar(255) NOT NULL,
									  `SEGMENT_DEF_ID` char(26) NOT NULL,
									  `PROCESS_ID` char(26) NOT NULL
									) ENGINE=InnoDB DEFAULT CHARSET=latin1;")) {
			// Set.
			$r = TRUE;
		}
		// Return.
		return $r;
	}
	
	// Create DQSEGDB DB.
	private function create_dqsegdb_db() {
		// Init.
		$r = FALSE;
		// Create PDO object
		$this->db_connect();
		// Alter DB structure.
		if($this->pdo->query("CREATE TABLE IF NOT EXISTS `tbl_dq_flags` (
								`dq_flag_id` int(11) NOT NULL AUTO_INCREMENT,
								`dq_flag_name` text NOT NULL,
								`dq_flag_ifo` int(11) NOT NULL DEFAULT '0',
								`dq_flag_assoc_versions` text NOT NULL,
								`dq_flag_active_means_ifo_badness` tinyint(1) DEFAULT NULL,
								`dq_flag_creator` int(11) DEFAULT NULL,
								`dq_flag_date_created` double NOT NULL,
								`PROCESS_ID` varchar(26) NOT NULL,
								`SEGMENT_DEF_ID` varchar(26) NOT NULL,
								PRIMARY KEY (`dq_flag_id`),
								KEY `dq_flag_active_means_ifo_badness` (`dq_flag_active_means_ifo_badness`),
								KEY `dq_flag_ifo` (`dq_flag_ifo`),
								KEY `dq_flag_creator` (`dq_flag_creator`)
							  ) ENGINE=InnoDB  DEFAULT CHARSET=latin1;
							  CREATE TABLE IF NOT EXISTS `tbl_dq_flag_versions` (
								`dq_flag_version_id` int(11) NOT NULL AUTO_INCREMENT,
								`dq_flag_fk` int(11) NOT NULL DEFAULT '0',
								`dq_flag_description` text NOT NULL,
								`dq_flag_version` int(11) NOT NULL DEFAULT '0',
								`dq_flag_version_known_segment_total` int(11) NOT NULL DEFAULT '0',
								`dq_flag_version_known_earliest_segment_time` double NOT NULL DEFAULT '0',
								`dq_flag_version_known_latest_segment_time` double NOT NULL DEFAULT '0',
								`dq_flag_version_active_segment_total` int(11) NOT NULL DEFAULT '0',
								`dq_flag_version_active_earliest_segment_time` double NOT NULL DEFAULT '0',
								`dq_flag_version_active_latest_segment_time` double NOT NULL DEFAULT '0',
								`dq_flag_version_deactivated` int(1) NOT NULL DEFAULT '0' COMMENT 'Is\r\nthis version unavailable?',
						  		`dq_flag_version_comment` text NOT NULL,
								`dq_flag_version_uri` text NOT NULL,
								`dq_flag_version_last_modifier` int(11) NOT NULL DEFAULT '0',
								`dq_flag_version_date_created` double NOT NULL,
								`dq_flag_version_date_last_modified` double NOT NULL,
								`PROCESS_ID` varchar(26) NOT NULL,
								`SEGMENT_DEF_ID` varchar(26) NOT NULL,
								PRIMARY KEY (`dq_flag_version_id`),
								KEY `dq_flag_version_creator` (`dq_flag_version`),
								KEY `dq_flag_fk` (`dq_flag_fk`),
								KEY `dq_flag_versio_unavailable` (`dq_flag_version_deactivated`),
								KEY `dq_flag_version_last_modifier` (`dq_flag_version_last_modifier`)
							  ) ENGINE=InnoDB  DEFAULT CHARSET=latin1;
							  CREATE TABLE IF NOT EXISTS `tbl_processes_tmp` (
								`process_id` int(11) NOT NULL AUTO_INCREMENT,
								`dq_flag_version_fk` int(11) NOT NULL DEFAULT '0',
								`process_full_name` text NOT NULL,
								`pid` int(11) NOT NULL DEFAULT '0',
								`fqdn` text NOT NULL,
								`version_comment` text NOT NULL,
								`user_fk` int(11) NOT NULL DEFAULT '0',
								`insertion_time` double NOT NULL DEFAULT '0',
								`affected_active_data_segment_total` int(11) NOT NULL DEFAULT '0',
								`affected_active_data_start` double NOT NULL DEFAULT '0',
								`affected_active_data_stop` double NOT NULL DEFAULT '0',
								`affected_known_data_segment_total` int(11) NOT NULL DEFAULT '0',
								`affected_known_data_start` double NOT NULL DEFAULT '0',
								`affected_known_data_stop` double NOT NULL DEFAULT '0',
								`process_time_started` double NOT NULL DEFAULT '0',
								`process_time_last_used` double NOT NULL DEFAULT '0',
								`PROCESS_ID_OLD` varchar(26) NOT NULL,
								PRIMARY KEY (`process_id`),
								KEY `user_fk` (`user_fk`),
								KEY `pid` (`pid`),
								KEY `dq_flag_version_fk` (`dq_flag_version_fk`)
							  ) ENGINE=InnoDB  DEFAULT CHARSET=latin1 ROW_FORMAT=COMPACT;
							  CREATE TABLE IF NOT EXISTS `tbl_processes` (
								`process_id` int(11) NOT NULL AUTO_INCREMENT,
								`dq_flag_version_fk` int(11) NOT NULL DEFAULT '0',
								`process_full_name` text NOT NULL,
								`pid` int(11) NOT NULL DEFAULT '0',
								`fqdn` text NOT NULL,
								`version_comment` text NOT NULL,
								`user_fk` int(11) NOT NULL DEFAULT '0',
								`insertion_time` double NOT NULL DEFAULT '0',
								`affected_active_data_segment_total` int(11) NOT NULL DEFAULT '0',
								`affected_active_data_start` double NOT NULL DEFAULT '0',
								`affected_active_data_stop` double NOT NULL DEFAULT '0',
								`affected_known_data_segment_total` int(11) NOT NULL DEFAULT '0',
								`affected_known_data_start` double NOT NULL DEFAULT '0',
								`affected_known_data_stop` double NOT NULL DEFAULT '0',
								`process_time_started` double NOT NULL DEFAULT '0',
								`process_time_last_used` double NOT NULL DEFAULT '0',
								`PROCESS_ID_OLD` varchar(26) NOT NULL,
								PRIMARY KEY (`process_id`),
								KEY `user_fk` (`user_fk`),
								KEY `pid` (`pid`),
								KEY `dq_flag_version_fk` (`dq_flag_version_fk`)
							  ) ENGINE=InnoDB  DEFAULT CHARSET=latin1 ROW_FORMAT=COMPACT;
							  CREATE TABLE IF NOT EXISTS `tbl_process_args` (
								`process_arg_id` int(11) NOT NULL AUTO_INCREMENT,
								`process_fk` int(11) NOT NULL DEFAULT '0',
								`process_argv` text NOT NULL,
								PRIMARY KEY (`process_arg_id`),
								KEY `process_fk` (`process_fk`)
							  ) ENGINE=InnoDB  DEFAULT CHARSET=latin1 COMMENT='Arguments passed by the process';
							  CREATE TABLE IF NOT EXISTS `tbl_segments` (
								`dq_flag_version_fk` int(11) NOT NULL,
								`segment_start_time` double NOT NULL,
								`segment_stop_time` double NOT NULL,
								`PROCESS_ID` varchar(26) NOT NULL,
								`SEGMENT_DEF_ID` varchar(26) NOT NULL,
								KEY `dq_flag_version_fk` (`dq_flag_version_fk`)
							  ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
							  CREATE TABLE IF NOT EXISTS `tbl_segment_summary` (
								`dq_flag_version_fk` int(11) NOT NULL DEFAULT '0',
								`segment_start_time` double NOT NULL,
								`segment_stop_time` double NOT NULL,
								`version_uri` text NOT NULL,
								`PROCESS_ID` varchar(26) NOT NULL,
								`SEGMENT_DEF_ID` varchar(26) NOT NULL,
								KEY `dq_flag_version_fk` (`dq_flag_version_fk`)
							  ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
							  CREATE TABLE IF NOT EXISTS `tbl_values` (
								`value_id` int(11) NOT NULL AUTO_INCREMENT,
								`value_group_fk` int(11) NOT NULL DEFAULT '0',
								`value_txt` text NOT NULL,
								PRIMARY KEY (`value_id`),
								KEY `value_group_fk` (`value_group_fk`)
							  ) ENGINE=InnoDB  DEFAULT CHARSET=latin1;
							  INSERT INTO `tbl_values` (`value_id`, `value_group_fk`, `value_txt`) VALUES
													   (1, 1, 'V1'),
													   (2, 1, 'H1'),
													   (3, 1, 'L1'),
													   (4, 3, 'ASCII'),
													   (5, 3, 'LIGOLW XML'),
													   (6, 1, 'G1'),
													   (7, 1, 'H2'),
													   (8, 1, 'P1');
							  CREATE TABLE IF NOT EXISTS `tbl_value_groups` (
								`value_group_id` int(11) NOT NULL AUTO_INCREMENT,
								`value_group` text NOT NULL,
								PRIMARY KEY (`value_group_id`)
							  ) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=4;
							  INSERT INTO `tbl_value_groups` (`value_group_id`, `value_group`) VALUES
															 (1, 'IFO'),
															 (2, 'User'),
															 (3, 'Data format');")) {
			// Set.
			$r = TRUE;
		}
		// Return.
		return $r;
	}
	
	// Import segdb CSV data.
	private function import_segdb_csv_data() {
		// Init.
		$r = FALSE;
		// Initialise.
		$constant = new Constants();
		$log = new Logger();
		// Log.
		$log->write_to_log("Sourcing segdb CSV files...");
		// Get source file dir.
		$constant->source_constants();
		// If the directory does not exist or is not a directory.
		if(!is_dir($constant->source_dir)) {
			// Log.
			$log->write_to_log("ERROR - ".$constant->source_dir." either does not exist, is not a directory or is not read-able.");
		}
		else {
			// Set.
			$sql = NULL;
			// Create PDO object
			$this->db_connect();
			// Scan directory.
			$a = scandir($constant->source_dir);
			// Loop.
			foreach($a as $file) {
				// Get table name.
				$e = explode('.', $file);
				$t = strtoupper($e[0]);
				// If table name exists and isn't README.
				if(!empty($t) && $t != 'README') {
					// Set SQL.
					$sql .= "LOAD DATA LOCAL INFILE '".$constant->source_dir.$file."' INTO TABLE ".$t." FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\n'; ";
					// Log.
					$log->write_to_log("Setting SQL to import CSV data for: ".$t);
				}
			}
			// If SQL has not been set.
			if(empty($sql)) {
				// Log.
				$log->write_to_log("ERROR: No CSV source files found.");
				// Set.
				$r = FALSE;
			}
			else {
				// Log.
				$log->write_to_log("Executing SQL statement to import from CSV to segdb...");
				// Foreach file, import contents to segdb.
				if($this->pdo->query($sql)) {
					// Log.
					$log->write_to_log("segdb CSV data successfully imported.");
					// Set.
					$r = TRUE;
				}
				else {
					// Log.
					$log->write_to_log("ERROR: unable to successfully import segdb CSV data: ".print_r($this->pdo->errorInfo()));
					// Set.
					$r = FALSE;
				}
			}
		}
		// Return.
		return $r;
	}
	
	// Alter schema, so as to cater for segdb IDs.
	private function alter_schema() {
		// Init.
		$r = FALSE;
		// Create PDO object
		$this->db_connect();
		// Alter DB structure.
		if($this->pdo->query("ALTER TABLE `tbl_dq_flags` ADD `PROCESS_ID` VARCHAR( 26 ) NOT NULL")) {
			if($this->pdo->query("ALTER TABLE `tbl_dq_flags` ADD `SEGMENT_DEF_ID` VARCHAR( 26 ) NOT NULL")) {
				if($this->pdo->query("ALTER TABLE `tbl_dq_flag_versions` ADD `PROCESS_ID` VARCHAR( 26 ) NOT NULL")) {
					if($this->pdo->query("ALTER TABLE `tbl_dq_flag_versions` ADD `SEGMENT_DEF_ID` VARCHAR( 26 ) NOT NULL")) {
						if($this->pdo->query("ALTER TABLE `tbl_processes` ADD `PROCESS_ID_OLD` VARCHAR( 26 ) NOT NULL")) {
							if($this->pdo->query("ALTER TABLE `tbl_segments` ADD `PROCESS_ID` VARCHAR( 26 ) NOT NULL")) {
								if($this->pdo->query("ALTER TABLE `tbl_segments` ADD `SEGMENT_DEF_ID` VARCHAR( 26 ) NOT NULL")) {
									if($this->pdo->query("ALTER TABLE `tbl_segment_summary` ADD `PROCESS_ID` VARCHAR( 26 ) NOT NULL")) {
										if($this->pdo->query("ALTER TABLE `tbl_segment_summary` ADD `SEGMENT_DEF_ID` VARCHAR( 26 ) NOT NULL")) {
											// Set.
											$r = TRUE;
										}
									}
								}
							}
						}
					}
				}
			}
		}
		// Return.
		return $r;
	}

	// Alter schema, so as to cater for segdb IDs.
	private function re_alter_schema() {
		// Init.
		$r = FALSE;
		// Instantiate.
		$log = new Logger();
		// Log.
		$log->write_to_log("Re-altering DB schema...");
		// Create PDO object
		$this->db_connect();
		// Alter DB structure.
		if($this->pdo->query("ALTER TABLE `tbl_dq_flags` DROP `PROCESS_ID`")) {
			if($this->pdo->query("ALTER TABLE `tbl_dq_flags` DROP `SEGMENT_DEF_ID`")) {
				if($this->pdo->query("ALTER TABLE `tbl_dq_flag_versions` DROP `PROCESS_ID`")) {
					if($this->pdo->query("ALTER TABLE `tbl_dq_flag_versions` DROP `SEGMENT_DEF_ID`")) {
						if($this->pdo->query("ALTER TABLE `tbl_processes` DROP `PROCESS_ID_OLD`")) {
							if($this->pdo->query("ALTER TABLE `tbl_processes` DROP `version_comment`")) {
								if($this->pdo->query("ALTER TABLE `tbl_segments` DROP `PROCESS_ID`")) {
									if($this->pdo->query("ALTER TABLE `tbl_segments` DROP `SEGMENT_DEF_ID`")) {
										if($this->pdo->query("ALTER TABLE `tbl_segment_summary` DROP `PROCESS_ID`")) {
											if($this->pdo->query("ALTER TABLE `tbl_segment_summary` DROP `version_uri`")) {
												if($this->pdo->query("ALTER TABLE `tbl_segment_summary` DROP `SEGMENT_DEF_ID`")) {
													if($this->pdo->query("DROP TABLE `tbl_processes_tmp`")) {
														if($this->pdo->query("DROP TABLE `PROCESS`")) {
															if($this->pdo->query("DROP TABLE `PROCESS_PARAMS`")) {
																if($this->pdo->query("DROP TABLE `SEGMENT`")) {
																	if($this->pdo->query("DROP TABLE `SEGMENT_DEFINER`")) {
																		if($this->pdo->query("DROP TABLE `SEGMENT_SUMMARY`")) {
																			// Set.
																			$r = TRUE;
																		}
																	}
																}
															}
														}
													}
												}
											}
										}
									}
								}
							}
						}
					}
				}
			}
		}
		// Return.
		return $r;
	}
	
	// Check, analyse and optimise each of the tables.
	private function db_optimisation() {
		// Init.
		$r = FALSE;
		// Initialise.
		$constant = new Constants();
		$log = new Logger();
		// Log.
		$log->write_to_log("Retrieving table names from DQSEGDB.");
		// Get DB name.
		$constant->db_connection_constants();
		// Create PDO object
		$this->db_connect();
		// Get tables.
		$res = $this->pdo->query("SHOW TABLES WHERE Tables_in_".$constant->db." LIKE 'tbl_%'");
		// Loop.
		while($loop = $res->fetch()) {
			// Set.
			$table = $loop[0];
			// Check tables.
			if($this->check_table($table)) {
				// Defragment tables.
				if($this->defragment_table($table)) {
					// Analyse tables.
					if($this->analyse_table($table)) {
						// Optimise tables.
						if($this->optimise_table($table)) {
							// Flush tables.
							if($this->flush_table($table)) {
								// Set.
								$r = TRUE;
							}
						}
					}
				}
			}
		}
		// Return.
		return $r;
	}
	
	// Check table.
	private function check_table($t) {
		// Init.
		$r = FALSE;
		// If arg passed.
		if(isset($t)) {
			// Create PDO object
			$this->db_connect();
			// Initialise.
			$log = new Logger();
			// Log.
			$log->write_to_log("Checking table: ".$t);
			// Create PDO object
			$this->db_connect();
			// Get tables.
			$res = $this->pdo->query("CHECK TABLE ".$t);
			// Loop.
			while($loop = $res->fetch()) {
				// Check tables.
				if($loop['Msg_text'] == 'OK') {
					// Record error.
					$log->write_to_log("Table checked successfully: ".$t);
					// Set.
					$r = TRUE;
				}
				else {
					// Record error.
					$log->write_to_log("ERROR: Unable to check table: ".$t);
				}
			}
		}
		// Return.
		return $r;
	}

	// Defragment table.
	private function defragment_table($t) {
		// Init.
		$r = FALSE;
		// If arg passed.
		if(isset($t)) {
			// Create PDO object
			$this->db_connect();
			// Initialise.
			$log = new Logger();
			// Log.
			$log->write_to_log("Defragmenting table: ".$t);
			// Create PDO object
			$this->db_connect();
			// Get tables.
			if($this->pdo->query("ALTER TABLE ".$t." ENGINE = INNODB")) {
				// Record error.
				$log->write_to_log("Table defragmented successfully: ".$t);
				// Set.
				$r = TRUE;
			}
			else {
				// Record error.
				$log->write_to_log("ERROR: Unable to check table: ".$t);
			}
		}
		// Return.
		return $r;
	}
	
	// Analyse table.
	private function analyse_table($t) {
		// Init.
		$r = FALSE;
		// If arg passed.
		if(isset($t)) {
			// Create PDO object
			$this->db_connect();
			// Initialise.
			$log = new Logger();
			// Log.
			$log->write_to_log("Analysing table: ".$t);
			// Create PDO object
			$this->db_connect();
			// Get tables.
			$res = $this->pdo->query("ANALYZE TABLE ".$t);
			// Loop.
			while($loop = $res->fetch()) {
				// Check tables.
				if($loop['Msg_text'] == 'OK') {
					// Record error.
					$log->write_to_log("Table analysed successfully: ".$t);
					// Set.
					$r = TRUE;
				}
				else {
					// Record error.
					$log->write_to_log("ERROR: Unable to analyse table: ".$t);
				}
			}
		}
		// Return.
		return $r;
	}
	
	// Optimise table.
	private function optimise_table($t) {
		// Init.
		$r = FALSE;
		// If arg passed.
		if(isset($t)) {
			// Create PDO object
			$this->db_connect();
			// Initialise.
			$log = new Logger();
			// Log.
			$log->write_to_log("Optimising table: ".$t);
			// Create PDO object
			$this->db_connect();
			// Get tables.
			$res = $this->pdo->query("OPTIMIZE TABLE ".$t);
			// Loop.
			while($loop = $res->fetch()) {
				// Check tables.
				if($loop['Msg_text'] == 'OK') {
					// Record error.
					$log->write_to_log("Table optimised successfully: ".$t);
					// Set.
					$r = TRUE;
				}
			}
			// If OK not found.
			if(!$r) {
				// Record error.
				$log->write_to_log("ERROR: Unable to optimise table: ".$t);
			}
				
		}
		// Return.
		return $r;
	}
	
	// Flush table.
	private function flush_table($t) {
		// Init.
		$r = FALSE;
		// If arg passed.
		if(isset($t)) {
			// Create PDO object
			$this->db_connect();
			// Initialise.
			$log = new Logger();
			// Log.
			$log->write_to_log("Flushing table: ".$t);
			// Create PDO object
			$this->db_connect();
			// Get tables.
			if($this->pdo->query("FLUSH TABLE ".$t)) {
				// Record error.
				$log->write_to_log("Table flushed successfully: ".$t);
				// Set.
				$r = TRUE;
			}
			else {
				// Record error.
				$log->write_to_log("ERROR: Unable to flush table: ".$t);
			}
		}
		// Return.
		return $r;
	}
	
	// Insert all segdb IFO into DQSEGDB schema.
	private function insert_segdb_ifo_to_dqsegdb() {
		// Init.
		$r = FALSE;
		$i = 0;
		$z = 0;
		$a = array();
		// Get array of ifos already in database.
		$i_a = $this->get_value_array_by_group(1);
		// Create PDO object
		$this->db_connect();
		// Get all segment definers.
		$res = $this->pdo->query("SELECT IFOS
                   				  	 	FROM SEGMENT_DEFINER
		    					  	 	GROUP BY IFOS
									 	ORDER BY IFOS");
		// Loop.
		while($loop = $res->fetch()) {
			// Set.
			$IFOS = $loop['IFOS'];
			// If not already in the database.
			if(!in_array($IFOS, $i_a)) {
				$i++;
				// Build.
				$a[$i] = $IFOS;
			}
		}
		// If array set.
		if(!empty($a)) {
			// Count number of elements.
			$a_tot = count($a);
			// Loop user array.
			foreach($a as $key => $ifo) {
				// Build prepared statement.
				if(($stmt = $this->pdo->prepare("INSERT INTO tbl_values
												 (value_group_fk, value_txt)
												 VALUES
												 (1, :ifo)"))) {
					// Execute.
					if($stmt->execute(array(':ifo' => $ifo))) {
						// Increment insert counter.
						$z++;
					}
				}
			}
			// If number of inserts matches number of users in array.
			if($a_tot == $z) {
				// Set.
				$r = TRUE;
			}
			else {
				// Log.
				$this->body .= "<p> - Number of inserts into DQSEGDB (".$z.") does not match number of ifos (".$a_tot.") in segdb.</p>\n";
			}
		}
		elseif(empty($a) && $i == 0) {
			// Log.
			$this->body .= "<p> - No inserts to be made. Ifos are already available in database.</p>\n";
			// Set.
			$r = TRUE;
		}
		// Return.
		return $r;
	}
	
	
	// Insert all segdb users into DQSEGDB schema.
	private function insert_segdb_users_to_dqsegdb() {
		// Init.
		$r = FALSE;
		$i = 0;
		$z = 0;
		$a = array();
		// Get array of ifos already in database.
		$u_a = $this->get_value_array_by_group(2);
		// Create PDO object
		$this->db_connect();
		// Get all segment definers.
		$res = $this->pdo->query("SELECT USERNAME
                   				  	 	FROM PROCESS
		    					  	 	GROUP BY USERNAME
									 	ORDER BY USERNAME");
		// Loop.
		while($loop = $res->fetch()) {
			// Set.
			$USERNAME = $loop['USERNAME'];
			// If not already in the database.
			if(!in_array($USERNAME, $u_a)) {
				$i++;
				// Build.
				$a[$i] = $USERNAME;
			}
		}
		// If array set.
		if(!empty($a)) {
			// Count number of elements.
			$a_tot = count($a);
			// Loop user array.
			foreach($a as $key => $u) {
				// Build prepared statement.
				if(($stmt = $this->pdo->prepare("INSERT INTO tbl_values
												 (value_group_fk, value_txt)
												 VALUES
												 (2, :u)"))) {
					 // Execute.
					if($stmt->execute(array(':u' => $u))) {
						// Increment insert counter.
						$z++;
					}
				}
			}
			// If number of inserts matches number of users in array.
			if($a_tot == $z) {
				// Set.
				$r = TRUE;
			}
			else {
				// Log.
				$this->body .= "<p> - Number of inserts into DQSEGDB (".$z.") does not match number of users (".$a_tot.") in segdb.</p>\n";
			}
		}
		elseif(empty($a) && $i == 0) {
			// Log.
			$this->body .= "<p> - No inserts to be made. Users are already available in database.</p>\n";
			// Set.
			$r = TRUE;
		}
		// Return.
		return $r;
	}
	
	// Get segment definers.
	private function convert_segment_definers_to_flags() {

		$r = FALSE;
		$i = 0;
		$z = 0;
		$a = array();
		// Initialise.
		$tc = new TimeConversion();
		// Get IFO array.
		$i_a = $this->get_value_array_by_group(1);
		// Get User array.
		$u_a = $this->get_value_array_by_group(2);
		// Get process array.
		$p_a = $this->get_process_array();
		// Create PDO object
		$this->db_connect();
		// Get all segment definers.
		$res = $this->pdo->query("SELECT *
                   				  FROM SEGMENT_DEFINER
		    					  GROUP BY IFOS, NAME");
		// Loop.
		while($loop = $res->fetch()) {
			// Set.
			$i++;
			$PROCESS_ID = $loop['PROCESS_ID'];
			$SEGMENT_DEF_ID = $loop['SEGMENT_DEF_ID'];
			$IFO_ID = array_search($loop['IFOS'], $i_a);
			$NAME = $loop['NAME'];
			$VERSION = $loop['VERSION'];
			$COMMENT = $loop['COMMENT'];
			$INSERTION_TIME = $tc->unix2gps(strtotime($tc->convert_bespoke_segdb_datetimes($loop['INSERTION_TIME'])));
			$USER_ID = array_search($p_a[$PROCESS_ID]['USERNAME'], $u_a);
			// Build.
			$a[$i] = array('PROCESS_ID' => $PROCESS_ID,
						   'SEGMENT_DEF_ID' => $SEGMENT_DEF_ID,
						   'IFO_ID' => $IFO_ID,
						   'NAME' => $NAME,
						   'COMMENT' => $COMMENT,
						   'INSERTION_TIME' => $INSERTION_TIME,
						   'USER_ID' => $USER_ID);
		}
		// If array set.
		if(!empty($a)) {
			// Count number of elements.
			$a_tot = count($a);
			// Loop user array.
			foreach($a as $key => $s) {
				// Build prepared statement.
				if(($stmt = $this->pdo->prepare("INSERT INTO tbl_dq_flags
												 (dq_flag_name,
												  dq_flag_ifo,
												  dq_flag_assoc_versions,
												  dq_flag_active_means_ifo_badness,
												  dq_flag_creator,
												  dq_flag_date_created,
									  			  PROCESS_ID,
												  SEGMENT_DEF_ID)
												 VALUES
												 (:n, :i, '', 0, :u, :t, :p, :s)"))) {
					// Execute.
					if($stmt->execute(array(':n' => $s['NAME'],
											':i' => $s['IFO_ID'],
											':u' => $s['USER_ID'],
											':t' => $s['INSERTION_TIME'],
											':p' => $s['PROCESS_ID'],
											':s' => $s['SEGMENT_DEF_ID'],))) {
						// Increment insert counter.
						$z++;
					}
				}
			}
			// If number of inserts matches number of users in array.
			if($a_tot == $z) {
				// Set.
				$r = TRUE;
			}
			else {
				// Log.
				$this->body .= "<p> - Number of inserts into DQSEGDB (".$z.") does not match number of segment definers, grouped by IFOS and NAME (".$a_tot.") in segdb.</p>\n";
			}
		}
		// Return.
		return $r;

//		return TRUE;
	}
	
	// Get flag array.
	private function get_flag_array() {
		// Init.
		$a = array();
		// Create PDO object
		$this->db_connect();
		// Get all segment definers.
		$res = $this->pdo->query("SELECT dq_flag_id, PROCESS_ID, SEGMENT_DEF_ID
                   				  FROM tbl_dq_flags
								  ORDER BY dq_flag_id");
		// Loop.
		while($loop = $res->fetch()) {
			// Set.
			$SEGMENT_DEF_ID = $loop['SEGMENT_DEF_ID'];
			// Build.
			$a[$SEGMENT_DEF_ID] = array('dq_flag_id' => $loop['dq_flag_id'], 'PROCESS_ID' => $loop['PROCESS_ID']);
		}
		// Return.
		return $a;
	}

	// Get process array.
	private function get_process_array() {
		// Init.
		$a = array();
		// Create PDO object
		$this->db_connect();
		// Get all segment definers.
		$res = $this->pdo->query("SELECT *
                   				  	 	FROM PROCESS");
		// Loop.
		while($loop = $res->fetch()) {
			// Set.
			$a[$loop['PROCESS_ID']] = array('USERNAME' => $loop['USERNAME']);
		}
		// Return.
		return $a;
	}
	
	// Get process ID array.
	private function get_process_id_array() {
		// Init.
		$a = array();
		// Create PDO object
		$this->db_connect();
		// Get all segment definers.
		$res = $this->pdo->query("SELECT process_id, dq_flag_version_fk, PROCESS_ID_OLD
                   				  FROM tbl_processes");
		// Loop.
		while($loop = $res->fetch()) {
			// Set.
			$a[$loop['PROCESS_ID_OLD']][$loop['dq_flag_version_fk']] = array('process_id' => $loop['process_id'], 'tot' => 0);
		}
		// Return.
		return $a;
	}
	// Get process version/ID array.
	private function get_process_version_id_total_array($sum, $s) {
		// Init.
		$a = $this->get_process_id_array();
		// Create PDO object
		$this->db_connect();
		// Get all segment definers.
		$res = $this->pdo->query("SELECT PROCESS_ID, dq_flag_version_fk, ".$s." AS 'tot'
                   				  FROM tbl_segment".$sum."
								  GROUP BY PROCESS_ID, dq_flag_version_fk");
		// Loop.
		while($loop = $res->fetch()) {
			// Set.
			$a[$loop['PROCESS_ID']][$loop['dq_flag_version_fk']]['tot'] = $loop['tot'];
		}
		// Return.
		return $a;
	}

	// Get full process array.
	private function get_full_process_array() {
		// Init.
		$a = array();
		// Initialise.
		$tc = new TimeConversion();
		// Get User array.
		$u_a = $this->get_value_array_by_group(2);
		// Get data format array.
		$i_a = $this->get_value_array_by_group(3);
		// Create PDO object
		$this->db_connect();
		// Get all segment definers.
		$res = $this->pdo->query("SELECT *
                   				  FROM PROCESS");
		// Loop.
		while($loop = $res->fetch()) {
			// Set.
			$version = $loop['VERSION'];
			if(!empty($version)) {
				$version = " (".$version.")";
			}
			$process_full_name = $loop['PROGRAM'].$version;
			if($process_full_name == '') {
				$process_full_name = '-';
			}
			$pid = $loop['UNIX_PROCID'];
			$fqdn = $loop['NODE'];
			$insertion_time = $tc->unix2gps(strtotime($tc->convert_bespoke_segdb_datetimes($loop['INSERTION_TIME'])));
			$user_fk = array_search($loop['USERNAME'], $u_a);
			$version_comment = $loop['COMMENT'];
			$process_time_started = $loop['START_TIME'];
			$process_time_last_used = $loop['END_TIME'];
			if(empty($process_time_last_used)) {
				$process_time_last_used = 0;
			}
			// Build.
			$a[$loop['PROCESS_ID']] = array('process_full_name' => $process_full_name,
											'pid' => $pid,
											'fqdn' => $fqdn,
											'version_comment' => $version_comment,
											'insertion_time' => $insertion_time,
											'user_fk' => $user_fk,
											'process_time_started' => $process_time_started,
											'process_time_last_used' => $process_time_last_used);
		}
		// Return.
		return $a;
	}
	
	// Get a process detail.
	private function get_process_detail($f, $p) {
		// Init.
		$r = NULL;
		// If args passed.
		if(isset($f) && isset($p)) {
			// Create PDO object
			$this->db_connect();
			// Build prepared statement.
			if(($stmt = $this->pdo->prepare("SELECT ".$f."
											 FROM PROCESS
											 WHERE PROCESS_ID=:p
											 LIMIT 1"))) {
				// Execute.
				if($stmt->execute(array(':p' => $p))) {
					// Loop.
					$res = $stmt;
					// Bind by column name.
					$res->bindColumn($f, $val);
					// Loop.
					while($res->fetch()) {
						// Set.
						$r = $val;
					}
				}
			}
		}
		// Return.
		return $r;
	} 
	
	// Get value ID by string.
	public function get_value_id_by_string($v) {
		// Init.
		$r = 0;
		// If arg passed.
		if(isset($v)) {
			// Create PDO object
			$this->db_connect();
			// Build prepared statement.
			if(($stmt = $this->pdo->prepare("SELECT value_id
											 FROM tbl_values
											 WHERE value_txt LIKE :v
											 LIMIT 1"))) {
				// Execute.
				if($stmt->execute(array(':v' => $v))) {
					// Loop.
					$res = $stmt;
					// Bind by column name.
					$res->bindColumn('value_id', $value_id);
					// Loop.
					while($res->fetch()) {
						// Set.
						$r = $value_id;
					}
				}
			}
		}
		// Return.
		return $r;
	}
	
	// Get value array by group.
	public function get_value_array_by_group($g) {
		// Init.
		$a = array();
		// If arg passed.
		if(isset($g)) {
			// Create PDO object
			$this->db_connect();
			// Build prepared statement.
			if(($stmt = $this->pdo->prepare("SELECT *
											 FROM tbl_values
											 WHERE value_group_fk=:g
											 ORDER BY value_id"))) {
				// Execute.
				if($stmt->execute(array(':g' => $g))) {
					// Loop.
					$res = $stmt;
					// Bind by column name.
					$res->bindColumn('value_id', $value_id);
					$res->bindColumn('value_txt', $value_txt);
					// Loop.
					while($res->fetch()) {
						// Set.
						$a[$value_id] = $value_txt;
					}
				}
			}
		}
		// Return.
		return $a;
	}
	
	// Convert segment definers to versions.
	private function convert_segment_definers_to_versions() {

		// Init.
		$r = FALSE;
		$i = 0;
		$z = 0;
		$a = array();
		// Initialise.
		$tc = new TimeConversion();
		// Get User array.
		$u_a = $this->get_value_array_by_group(2);
		// Get Ifo array.
		$i_a = $this->get_value_array_by_group(1);
		// Get process array.
		$p_a = $this->get_process_array();
		// Create PDO object
		$this->db_connect();
		// Get all segment definers.
		$res = $this->pdo->query("SELECT *
                   				  FROM SEGMENT_DEFINER");
		// Loop.
		while($loop = $res->fetch()) {
			// Set.
			$i++;
			$PROCESS_ID = $loop['PROCESS_ID'];
			$SEGMENT_DEF_ID = $loop['SEGMENT_DEF_ID'];
			$VERSION = $loop['VERSION'];
			$COMMENT = $loop['COMMENT'];
			$INSERTION_TIME = $tc->unix2gps(strtotime($tc->convert_bespoke_segdb_datetimes($loop['INSERTION_TIME'])));
			$USER_ID = array_search($p_a[$PROCESS_ID]['USERNAME'], $u_a);
			$IFO_ID = array_search($loop['IFOS'], $i_a);
			$dq_flag_fk = $this->get_flag_id_from_ifo_and_name($IFO_ID, $loop['NAME']);
			// Build.
			$a[$i] = array('PROCESS_ID' => $PROCESS_ID,
						   'SEGMENT_DEF_ID' => $SEGMENT_DEF_ID,
						   'version' => $VERSION,
						   'description' => $COMMENT,
						   'date_created' => $INSERTION_TIME,
						   'last_modifier' => $USER_ID,
						   'dq_flag_fk' => $dq_flag_fk);
		}
		// If array set.
		if(!empty($a)) {
			// Count number of elements.
			$a_tot = count($a);
			// Loop flag array.
			foreach($a as $key => $s) {
				// Build prepared statement.
				if(($stmt = $this->pdo->prepare("INSERT INTO tbl_dq_flag_versions
												 (dq_flag_fk,
												  dq_flag_description,
												  dq_flag_version,
												  dq_flag_version_last_modifier,
												  dq_flag_version_date_created,
												  dq_flag_version_date_last_modified,
												  PROCESS_ID,
												  SEGMENT_DEF_ID)
												 VALUES
												 (:f, :d, :v, :u, :dc, :dm, :p, :s)"))) {
					// Execute.
					if($stmt->execute(array(':f' => $s['dq_flag_fk'],
											':d' => $s['description'],
											':v' => $s['version'],
											':u' => $s['last_modifier'],
											':dc' => $s['date_created'],
											':dm' => $s['date_created'],
											':p' => $s['PROCESS_ID'],
											':s' => $s['SEGMENT_DEF_ID']))) {
						// Increment insert counter.
						$z++;
					}
				}
			}
			// If number of inserts matches number of users in array.
			if($a_tot == $z) {
				// Set.
				$r = TRUE;
			}
			else {
				// Log.
				$this->body .= "<p> - Number of inserts into DQSEGDB (".$z.") does not match number of segment definers (".$a_tot.") in segdb.</p>\n";
			}
		}
		// Return.
		return $r;

//		return TRUE;
	}

	// Get a DQSEGDB flag ID from its segdb ifo and name.
	private function get_flag_id_from_ifo_and_name($i, $n) {
		// Init.
		$r = NULL;
		// If args passed.
		if(isset($i) && isset($n)) {
			// Create PDO object
			$this->db_connect();
			// Get.
			if(($stmt = $this->pdo->prepare("SELECT dq_flag_id
											 FROM tbl_dq_flags
											 WHERE dq_flag_ifo=:i AND dq_flag_name LIKE :n
											 LIMIT 1"))) {
				// Execute.
				if($stmt->execute(array(':i' => $i, ':n' => $n))) {
					// Loop.
					$res = $stmt;
					// Bind by column name.
					$res->bindColumn('dq_flag_id', $dq_flag_id);
					// Loop.
					while($res->fetch()) {
						// Set.
						$r = $dq_flag_id;
					}
				}
			}
		}
		// Return.
		return $r;
	}

	// Associate versions.
	private function associate_versions() {
		$r = FALSE;
		$z = 0;
		$a = array();
		// Create PDO object
		$this->db_connect();
		// Get all segment definers.
		$res = $this->pdo->query("SELECT dq_flag_fk, dq_flag_version
                 				  FROM tbl_dq_flag_versions
		    					  ORDER BY dq_flag_fk, dq_flag_version");
		// Loop.
		while($loop = $res->fetch()) {
			// Set.
			$dq_flag_fk = $loop['dq_flag_fk'];
			$dq_flag_version = $loop['dq_flag_version'];
			// Set array.
			if(!isset($a[$dq_flag_fk])) {
				$a[$dq_flag_fk] = array();
			}
			// Add to array.
			array_push($a[$dq_flag_fk], $dq_flag_version);
		}
		// Count elements in array.
		$a_tot = count($a);
		// Make sure that versions are not duplicated, but emptying the field as it stands.
		$res = $this->pdo->query("UPDATE tbl_dq_flags
								  SET dq_flag_assoc_versions=''");		
		// Loop the array.
		foreach($a as $flag_id => $version_array) {
			// Set.
			$csv = implode(",", $version_array);
			// Update the associated versions field.
			if(($stmt = $this->pdo->prepare("UPDATE tbl_dq_flags
											 SET dq_flag_assoc_versions=:c
											 WHERE dq_flag_id=:f"))) {
				// Execute.
				if($stmt->execute(array(':c' => $csv, ':f' => $flag_id))) {
					// Set.
					$z++;
				}
			}
		}
		// If number of updates matches number of elements in array.
		if($a_tot == $z) {
			// Set.
			$r = TRUE;
		}
		else {
			// Log.
			$this->body .= "<p> - Number of updates of associated versions (".$z.") does not match number of elements in array retrieved (".$a_tot.").</p>\n";
		}
		// Return.
		return $r;
	}
	
	// Associate process args.
	private function associate_process_args() {
		// Init.
		$r = TRUE;
		$h = 0;
		$i = 0;
		$p_a = array();
		// Initialise.
		$log = new Logger();
		// Create PDO object
		$this->db_connect();
		// Log.
		$log->write_to_log("Retrieving params from segdb.");
		// Get params from segdb.
		$res = $this->pdo->query("SELECT PROCESS_ID, PARAM, VALUE
                   		  	 	  FROM PROCESS_PARAMS
								  ORDER BY PROCESS_ID, INSERTION_TIME");
		// Loop.
		while($loop = $res->fetch()) {
			// Set.
			$PROCESS_ID = $loop['PROCESS_ID'];
			$PARAM = $loop['PARAM'];
			$VALUE = $loop['VALUE'];
			// If array does not yet exist.
			if(!isset($p_a[$PROCESS_ID])) {
				// Set as array.
				$p_a[$PROCESS_ID] = array();
			}
			// Push to array.
			array_push($p_a[$PROCESS_ID], $PARAM);
			array_push($p_a[$PROCESS_ID], $VALUE);
		}
		// If array empty.
		if(empty($p_a)) {
			// Log.
			$log->write_to_log("ERROR - segdb param array not set.");
			// Set result to error.
			$r = FALSE;
		}
		// Otherwise, if array filled.
		else {
			// Log.
			$log->write_to_log("Retrieving params...");
			// Get old and new process IDs from DQSEGDB.
			$res = $this->pdo->query("SELECT process_id, PROCESS_ID_OLD
	                   		 		  FROM tbl_processes
									  ORDER BY PROCESS_ID_OLD, process_id");
			// Loop.
			while($loop = $res->fetch()) {
				// Set.
				$process_id = $loop['process_id'];
				$PROCESS_ID_OLD = $loop['PROCESS_ID_OLD'];
				// If key exists in Param array.
				if(array_key_exists($PROCESS_ID_OLD, $p_a)) {
					// Loop all available params.
					foreach($p_a[$PROCESS_ID_OLD] as $key => $arg) {
						// Insert param as arg for this process ID into DQSEGDB.
						if(($stmt = $this->pdo->prepare("INSERT INTO
														 tbl_process_args
														 (process_fk, process_argv)
														 VALUES
														 (:pid, :v)"))) {
							// Execute.
							if($stmt->execute(array(':pid' => $process_id,
													':v' => $arg))) {
							}
							// Otherwise.
							else {
								// Log.
								$log->write_to_log("ERROR - Problem associating process args: ".$stmt->errorInfo[2]);
								// Set result to error.
								$r = FALSE;
							}
						}
					}
				}
			}
		}
/*
 		// Log.
		$log->write_to_log("Retrieving process IDs from segdb params table...");
		// Get new and old process IDs from process table.
		$res = $this->pdo->query("SELECT PARAM, VALUE
                   		  	 			FROM PROCESS_PARAMS
										ORDER BY PROCESS_ID, INSERTION_TIME");
		// Loop.
		while($loop = $res->fetch()) {
			// Set array.
			$p_a[$loop['PROCESS_ID']] = array();
		}
		// If array has not been set.
		if(empty($p_a)) {
			// Log.
			$log->write_to_log("ERROR - Problem setting initial process array.");
			// Set result to error.
			$r = FALSE;
		}
		// Loop through old processes.
		foreach($p_a as $PROCESS_ID_OLD => $process_id_array) {
			// Log.
			$log->write_to_log("Retrieving params for PROCESS_ID (".$PROCESS_ID_OLD.")");
			unset($param_a);
			$param_a = array();
			// Retrieve process arg information from segdb.
			$res = $this->pdo->query("SELECT PARAM, VALUE
											FROM PROCESS_PARAMS
											WHERE PROCESS_ID=".$PROCESS_ID_OLD."
											ORDER BY INSERTION_TIME");
			// Execute.
			while($loop = $res->fetch()) {
				// Push arg and value.
				array_push($param_a, $loop['PARAM']);
				array_push($param_a, $loop['VALUE']);
			}
			// Loop through new process ID array.
			foreach($process_id_array as $key => $process_id) {
				// Log.
				$log->write_to_log("Setting for process insertion (".$process_id.")".print_r($param_a));
				// Loop through parameter array.
				foreach($param_a as $k => $value) {
					// Log.
					$log->write_to_log("Writing params for process (".$PROCESS_ID_OLD.", ".$process_id.")");
					// Insert information into DQSEGDB.
					if(($stmt = $this->pdo->prepare("INSERT INTO
													 tbl_process_args
													 (process_fk, process_argv)
													 VALUES
													 (:pid, :v)"))) {
						// Execute.
						if($stmt->execute(array(':pid' => $process_id,
												':v' => $value))) {
						}
						// Otherwise.
						else {
							// Log.
							$log->write_to_log("ERROR - Problem associating process args: ".$stmt->errorInfo[2]);
							// Set result to error.
							$r = FALSE;
						}
					}
				}
			}
		}
*/		
		// Log.
		$log->write_to_log("Finished process-arg association.");
		// Return.
		return $r;
	}
	
	// Convert processes.
	private function convert_processes() {
		// Init.
		$r = TRUE;
		$i = 0;
		// Initialise.
		$log = new Logger();
		// Create PDO object
		$this->db_connect();
		// Log.
		$log->write_to_log("Beginning process conversion...");
		// Log.
		$log->write_to_log("Retrieving segdb processes...");
		// Get full segdb process array.
		$p_a = $this->get_full_process_array();
		// Log.
		$log->write_to_log("Retrieving version and process IDs from DQSEGDB segment table...");
		// Get version_fks and associated PROCESS_IDs from segments table.
		$res = $this->pdo->query("SELECT dq_flag_version_fk, PROCESS_ID
                   		  	 	  FROM tbl_segments
								  GROUP BY PROCESS_ID, dq_flag_version_fk
								  ORDER BY dq_flag_version_fk");
		// Loop.
		while($loop = $res->fetch()) {
			// If on first loop.
			if($i == 0) {
				$i++;
				// Log.
				$log->write_to_log("Attempting to insert segdb process information into DQSEGDB...");
			}
			// Set.
			$v_id = $loop['dq_flag_version_fk'];
			$PROCESS_ID = $loop['PROCESS_ID'];
			$pfn = $p_a[$PROCESS_ID]['process_full_name'];
			if(empty($pfn)) {
				$pfn = '-';
			}
			// Insert version with process info to database.
			if(($stmt = $this->pdo->prepare("INSERT INTO tbl_processes_tmp
									  		 (dq_flag_version_fk, process_full_name, pid, fqdn, version_comment, user_fk, insertion_time, process_time_started, process_time_last_used, PROCESS_ID_OLD)
									 		 VALUES
							  				 (:v,:n,:p,:f,:c,:u,:i,:sta,:sto,:po)"))) {
				// Execute.
				if($stmt->execute(array(':v' => $v_id,
										':n' => $pfn,
										':p' => $p_a[$PROCESS_ID]['pid'],
										':f' => $p_a[$PROCESS_ID]['fqdn'],
										':c' => $p_a[$PROCESS_ID]['version_comment'],
										':u' => $p_a[$PROCESS_ID]['user_fk'],
										':i' => $p_a[$PROCESS_ID]['insertion_time'],
										':sta' => $p_a[$PROCESS_ID]['process_time_started'],
										':sto' => $p_a[$PROCESS_ID]['process_time_last_used'],
										':po' => $PROCESS_ID))) {
				}
				// Otherwise, output error.
				else {
					// Log.
					$log->write_to_log("ERROR - Problem inserting process information into DQSEGDB for: version (VERSION ID: ".$v_id."). ERROR INFO: ".print_r($stmt->errorInfo()));
				}
			}
		}
		// Log.
		$log->write_to_log("Finished process conversion.");
		// Return.
		return $r;
	}
	
	// Coalesce processes.
	private function coalesce_processes() {
		// Init.
		$r = TRUE;
		$g = NULL;
		// Initialise.
		$constant = new Constants();
		$log = new Logger();
		// Create PDO object
		$this->db_connect();
		// Get package execution constants.
		$constant->package_execution_constants();
		// If grouping.
		if($constant->use_process_coalescence) {
			$g = "GROUP BY pid, dq_flag_version_fk";
		}
		// Log.
		$log->write_to_log("Beginning process coalescence...");
		// Get version_fks and associated PROCESS_IDs from segments table.
		if($res = $this->pdo->query("INSERT INTO tbl_processes
								  	 (dq_flag_version_fk, process_full_name, pid, fqdn, version_comment, user_fk, insertion_time, process_time_started, process_time_last_used, PROCESS_ID_OLD)
								  	 SELECT dq_flag_version_fk, process_full_name, pid, fqdn, version_comment, user_fk, MIN(insertion_time) AS 'insertion_time', MIN(process_time_started) AS 'process_time_started', MAX(process_time_last_used) AS 'process_time_last_used', PROCESS_ID_OLD
                   		  	 	  	 FROM tbl_processes_tmp
								  	 ".$g."
								  	 ORDER BY dq_flag_version_fk")) {
			// Log.
			$log->write_to_log("Processes coalesced successfully.");
		}
		// Otherwise.
		else {
			// Log.
			$log->write_to_log("ERROR - Problem coalescing processes. ERROR INFO: ".print_r($this->pdo->errorInfo()));
			// Set.
			$r = FALSE;
		}
		// Log.
		$log->write_to_log("Finished coalescing processes.");
		// Return.
		return $r;
	}
		
	// Get all versions according to segdb PROCESS_ID or SEGMENT_DEF_ID.
	private function get_version_array($p_or_d) {
		// Init.
		$a = array();
		// If args passed.
		if(isset($p_or_d)) {
			// If PROCESS_ID.
			if($p_or_d) {
				$f = 'PROCESS_ID';
			}
			// Otherwise, if SEGMENT_DEF_ID.
			else {
				$f = 'SEGMENT_DEF_ID';
			}
			// Create PDO object
			$this->db_connect();
			// Get.
			$res = $this->pdo->query("SELECT ".$f.", dq_flag_version_id
									  FROM tbl_dq_flag_versions
									  ORDER BY dq_flag_version_id");
			while($loop = $res->fetch()) {
				// Set.
				$a[$loop[$f]] = $loop['dq_flag_version_id'];
			}
		}
		// Return.
		return $a;
	}
	
	// Get all versions according to segdb PROCESS_ID or SEGMENT_DEF_ID.
	private function get_dqsegdb_version_array() {
		// Init.
		$a = array();
		// Create PDO object
		$this->db_connect();
		// Get.
		$res = $this->pdo->query("SELECT dq_flag_version_id, dq_flag_version
								  FROM tbl_dq_flag_versions
								  ORDER BY dq_flag_version_id");
		while($loop = $res->fetch()) {
			// Set.
			$a[$loop['dq_flag_version_id']] = $loop['dq_flag_version'];
		}
		// Return.
		return $a;
	}
	
	// Update version comments.
	private function update_version_comments() {
		// Init.
		$r = FALSE;
		// Instantiate.
		$log = new Logger();
		// Log.
		$log->write_to_log("Updating version comments...");
		// Create PDO object.
		$this->db_connect();
		// Get.
		$res = $this->pdo->query("SELECT dq_flag_version_fk, version_comment
								  FROM tbl_processes_tmp
								  WHERE version_comment NOT LIKE ''
								  GROUP BY dq_flag_version_fk");
		// Loop.
		while($loop = $res->fetch()) {
			// Set.
			$v_id = $loop['dq_flag_version_fk'];
			$version_comment = $loop['version_comment'];
			// Insert segments.
			if(($stmt = $this->pdo->prepare("UPDATE tbl_dq_flag_versions
											 SET dq_flag_version_comment=:c
											 WHERE dq_flag_version_id=:v"))) {
				// Execute.
				if($stmt->execute(array(':c' => $version_comment, ':v' => $v_id))) {
					// Set.
					$r = TRUE;
				}
				// Otherwise, output error.
				else {
					// Log.
					$log->write_to_log("ERROR - Problem updating version comments: ".$stmt->errorInfo[2]);
				}
			}
		}
		// Log.
		$log->write_to_log("Finished updating version comments");
		// Return.
		return $r;
	}

	// Update version URI.
	private function update_version_uri() {
		// Init.
		$r = FALSE;
		// Instantiate.
		$log = new Logger();
		// Log.
		$log->write_to_log("Updating version URI...");
		// Create PDO object.
		$this->db_connect();
		// Get.
		$res = $this->pdo->query("SELECT dq_flag_version_fk, version_uri
								  FROM tbl_segment_summary
								  WHERE version_uri NOT LIKE ''
								  GROUP BY dq_flag_version_fk");
		// Loop.
		while($loop = $res->fetch()) {
			// Set.
			$v_id = $loop['dq_flag_version_fk'];
			$version_uri = $loop['version_uri'];
			// Insert segments.
			if(($stmt = $this->pdo->prepare("UPDATE tbl_dq_flag_versions
											 SET dq_flag_version_uri=:u
											 WHERE dq_flag_version_id=:v"))) {
				// Execute.
				if($stmt->execute(array(':u' => $version_uri, ':v' => $v_id))) {
					// Set.
					$r = TRUE;
				}
				// Otherwise, output error.
				else {
					// Log.
					$log->write_to_log("ERROR - Problem updating version URI: ".$stmt->errorInfo[2]);
				}
			}
		}
		// Log.
		$log->write_to_log("Finished updating version URI");
		// Return.
		return $r;
	}
	
	// Update version-segment boundaries.
	private function update_version_segment_boundaries($ak, $max_min) {
		// Init.
		$r = TRUE;
		$t_a = "s";
		$t_b = "MIN(segment_start_time)";
		$t_c = "known";
		$t_d = "earliest";
		// If dealing with active.
		if($ak) {
			$t_a = "_summary";
			$t_c = "active";
		}
		// If dealing with latest segments.
		if($max_min) {
			$t_b = "MAX(segment_stop_time)";
			$t_d = "latest";
		}
		// Instantiate.
		$log = new Logger();
		// Log.
		$log->write_to_log("Updating ".$t_c." ".$t_d." version-segment boundaries...");
		// Create PDO object
		$this->db_connect();
		// Get.
		$res = $this->pdo->query("SELECT dq_flag_version_fk, ".$t_b." AS 'tot'
								  FROM tbl_segment".$t_a."
								  GROUP BY dq_flag_version_fk");
		// Loop.
		while($loop = $res->fetch()) {
			// Set.
			$tot = $loop['tot'];
			$v_id = $loop['dq_flag_version_fk'];
			// Insert segments.
			if(($stmt = $this->pdo->prepare("UPDATE tbl_dq_flag_versions
											 SET dq_flag_version_".$t_c."_".$t_d."_segment_time=:t
											 WHERE dq_flag_version_id=:v"))) {
				// Execute.
				if($stmt->execute(array(':t' => $tot,
										':v' => $v_id))) {
				}
				// Otherwise, output error.
				else {
					// Log.
					$log->write_to_log("ERROR - Problem updating ".$t_c." ".$t_d." version-segment boundaries");
					// Set result to error to not automatically go on with segment summary insertion.
//						$r = FALSE;
				}
			}
		}
		// Log.
		$log->write_to_log("Finished updating ".$t_c." ".$t_d." version-segment boundaries");
		// Return.
		return $r;
	}
	
	// Update process-segment boundaries.
	private function update_process_segment_boundaries($ak, $max_min) {
		// Init.
		$r = TRUE;
		$t_a = "s";
		$t_b = "MIN(segment_start_time)";
		$t_c = "known";
		$t_d = "start";
		// If dealing with active.
		if($ak) {
			$t_a = "_summary";
			$t_c = "active";
		}
		// If dealing with latest segments.
		if($max_min) {
			$t_b = "MAX(segment_stop_time)";
			$t_d = "stop";
		}
		// Instantiate.
		$log = new Logger();
		// Log.
		$log->write_to_log("Updating ".$t_c." ".$t_d." process-segment boundaries...");
		// Get process version/ID array.
		$p_a = $this->get_process_version_id_total_array($t_a, $t_b);
		// Log.
		$log->write_to_log("Process IDs and ".$t_c." ".$t_d." process-segment boundaries retrieved.");
		// Log.
		$log->write_to_log("Beginning write to database...");
		// Create PDO object
		$this->db_connect();
		// Loop through old process ID array.
		foreach($p_a as $p => $p_array) {
			// Loop through version array.
			foreach($p_array as $v => $v_array) {
				// If the process ID has been set.
				if(isset($v_array['process_id'])) {
					// Set.
					$p = $v_array['process_id'];
					$tot = $v_array['tot'];
						// Update totals.
					if(($stmt = $this->pdo->prepare("UPDATE tbl_processes
													 SET affected_".$t_c."_data_".$t_d."=:t
													 WHERE process_id=:p"))) {
						// Execute.
						if($stmt->execute(array(':t' => $tot,
												':p' => $p))) {
						}
						// Otherwise, output error.
						else {
							// Log.
							$log->write_to_log("ERROR - Problem updating process ".$t_c." segment boundaries.");
						}
					}
				}
			}
		}
		// Log.
		$log->write_to_log("Finished updating process ".$t_c." ".$t_d."-segment boundaries");
		// Return.
		return $r;
	}
	
	// Update process segment totals.
	private function update_process_segment_totals($ak) {
		// Init.
		$r = TRUE;
		$t_a = "s";
		$t_b = "COUNT(dq_flag_version_fk)";
		$t_c = "known";
		// If dealing with active.
		if($ak) {
			$t_a = "_summary";
			$t_c = "active";
		}
		// Instantiate.
		$log = new Logger();
		// Log.
		$log->write_to_log("Updating ".$t_c." process-segment totals...");
		// Get process version/ID array.
		$p_a = $this->get_process_version_id_total_array($t_a, $t_b);
		// Log.
		$log->write_to_log("Process IDs and ".$t_c." process-segment totals retrieved.");
		// Log.
		$log->write_to_log("Beginning write to database...");
		// Create PDO object
		$this->db_connect();
		// Loop through old process ID array.
		foreach($p_a as $p => $p_array) {
			// Loop through version array.
			foreach($p_array as $v => $v_array) {
				// If the process ID has been set.
				if(isset($v_array['process_id'])) {
					// Set.
					$p = $v_array['process_id'];
					$tot = $v_array['tot'];
						// Update totals.
					if(($stmt = $this->pdo->prepare("UPDATE tbl_processes
													 SET affected_".$t_c."_data_segment_total=:t
													 WHERE process_id=:p"))) {
						// Execute.
						if($stmt->execute(array(':t' => $tot,
												':p' => $p))) {
						}
						// Otherwise, output error.
						else {
							// Log.
							$log->write_to_log("ERROR - Problem updating process ".$t_c." segment totals.");
						}
					}
				}
			}
		}
		// Log.
		$log->write_to_log("Finished updating ".$t_c." process-segment totals.");
		// Return.
		return $r;
	}

	// Update version-segment totals.
	private function update_version_segment_totals($ak) {
		// Init.
		$r = TRUE;
		$t_a = "s";
		$t_c = "known";
		// If dealing with active.
		if($ak) {
			$t_a = "_summary";
			$t_c = "active";
		}
		// Instantiate.
		$log = new Logger();
		// Log.
		$log->write_to_log("Updating ".$t_c." version-segment totals...");
		// Create PDO object
		$this->db_connect();
		// Get.
		$res = $this->pdo->query("SELECT dq_flag_version_fk, COUNT(dq_flag_version_fk) AS 'tot'
								  FROM tbl_segment".$t_a."
								  GROUP BY dq_flag_version_fk");
		// Loop.
		while($loop = $res->fetch()) {
			// Set.
			$tot = $loop['tot'];
			$v_id = $loop['dq_flag_version_fk'];
			// Insert segments.
			if(($stmt = $this->pdo->prepare("UPDATE tbl_dq_flag_versions
											 SET dq_flag_version_".$t_c."_segment_total=:t
											 WHERE dq_flag_version_id=:v"))) {
				// Execute.
				if($stmt->execute(array(':t' => $tot,
										':v' => $v_id))) {
				}
				// Otherwise, output error.
				else {
					// Log.
					$log->write_to_log("ERROR - Problem updating ".$t_c." version-segment totals...");
					// Set result to error to not automatically go on with segment summary insertion.
//						$r = FALSE;
				}
			}
			// Log.
//			$log->write_to_log("Finished updating ".$t_c." segment totals for version: ".$v_id." (".$tot.")...");
		}
		// Log.
		$log->write_to_log("Finished updating ".$t_c." version-segment totals...");
		// Return.
		return $r;
	}
	
	// Count number of segments for use in import limits.
	private function count_segdb_segments($s) {
		// Init.
		$r = 0;
		$t = NULL;
		$f = NULL;
		// Instantiate.
		$log = new Logger();
		// If looking at summary table.
		if($s) {
			$t = "_SUMMARY";
			$f = "_SUM";
		}
		// Create PDO object
		$this->db_connect();
		// Get.
		$res = $this->pdo->query("SELECT COUNT(SEGMENT".$f."_ID) AS 'tot'
										FROM SEGMENT".$t);
		// Loop.
		while($loop = $res->fetch()) {
			// Set.
			$r = $loop['tot'];
		}
		// Log.
		$log->write_to_log("Upper segment import limit set at: ".$r);
		// Return.
		return $r;
	} 
	
	// Convert segments.
	private function convert_segments($s) {
		// Init.
		$r = TRUE;
		// Instantiate.
		$constant = new Constants();
		$log = new Logger();
		// Get conversion constant.
		$constant->package_execution_constants();
		// Log.
		$log->write_to_log("Converting segments/segment summaries...");
		// If not using joins in segment conversion.
		if(!$constant->use_join_in_segment_conversion) {
			// Init.
			$z = 1000000;
			$t_a = NULL;
			$t_b = "s";
			$t_c = NULL;
			// If dealing with summaries.
			if($s) {
				$t_a = "_SUMMARY";
				$t_b = "_summary";
				$t_c = " summaries";
			}
			// Log.
			$log->write_to_log("Converting segment".$t_c." without SQL JOIN...");
			// Get upper import limit.
			$limit = $this->count_segdb_segments($s);
			// Get version array.
			$v_a = $this->get_version_array(FALSE);
			// Create PDO object
			$this->db_connect();
			// Loop through until limit is reached.
			for($i=0; $i<$limit; $i=$i+$z) {
				// Log.
				$log->write_to_log("Extracting segment".$t_c."s (".$i.",".$z.")");
				// Get.
				$res = $this->pdo->query("SELECT *
										  FROM SEGMENT".$t_a."
										  LIMIT ".$i.",".$z);
				// Loop.
				while($loop = $res->fetch()) {
					// Set.
					$PROCESS_ID = $loop['PROCESS_ID'];
					$SEGMENT_DEF_ID = $loop['SEGMENT_DEF_ID'];
					$START_TIME = $loop['START_TIME'];
					$END_TIME = $loop['END_TIME'];
					// Get flag version id from SEGMENT_DEF_ID.
					$dq_flag_version_fk = $v_a[$SEGMENT_DEF_ID];
					// If dealing with summaries.
					if($s) {
						$COMMENT = $loop['COMMENT'];
					}
					// If dealing with 'known' (summaries).
					if($s) {
						// Insert segments.
						if(($stmt = $this->pdo->prepare("INSERT INTO tbl_segment_summary
														 (dq_flag_version_fk,
														  segment_start_time,
														  segment_stop_time,
														  version_uri,
														  PROCESS_ID,
														  SEGMENT_DEF_ID)
														 VALUES
														 (:v, :s, :e, :c, :p, :d)"))) {
							// Execute.
							if($stmt->execute(array(':v' => $dq_flag_version_fk,
													':s' => $START_TIME,
													':e' => $END_TIME,
													':c' => $COMMENT,
													':p' => $PROCESS_ID,
													':d' => $SEGMENT_DEF_ID))) {
							}
							// Otherwise, output error.
							else {
								// Log.
								$log->write_to_log("ERROR - Problem converting segment".$t_c."s (version_id: $dq_flag_version_fk, SEGMENT_DEF_ID: $SEGMENT_DEF_ID) - ".$stmt->errorInfo[2]);
								// Set result to error to not automatically go on with segment summary insertion.
								$r = FALSE;
							}
						}
					}
					// Otherwise, active.
					else {
						// Insert segments.
						if(($stmt = $this->pdo->prepare("INSERT INTO tbl_segments
														 (dq_flag_version_fk,
														  segment_start_time,
														  segment_stop_time,
														  PROCESS_ID,
														  SEGMENT_DEF_ID)
														 VALUES
														 (:v, :s, :e, :p, :d)"))) {
							// Execute.
							if($stmt->execute(array(':v' => $dq_flag_version_fk,
													':s' => $START_TIME,
													':e' => $END_TIME,
													':p' => $PROCESS_ID,
													':d' => $SEGMENT_DEF_ID))) {
							}
							// Otherwise, output error.
							else {
								// Log.
								$log->write_to_log("ERROR - Problem converting segment".$t_c."s (version_id: $dq_flag_version_fk, SEGMENT_DEF_ID: $SEGMENT_DEF_ID) - ".$stmt->errorInfo[2]);
								// Set result to error to not automatically go on with segment summary insertion.
								$r = FALSE;
							}
						}
					}
				}
			}
		}
		// If not using joins in segment conversion.
		else {
			// Init.
			$t_a = NULL;
			$t_b = "s";
			$t_c = "s";
			$t_d = NULL;
			$t_e = NULL;
			// If dealing with summaries.
			if($s) {
				$t_a = "_SUMMARY";
				$t_b = "_summary";
				$t_c = " summaries";
				$t_d = "COMMENT,";
				$t_e = "version_uri,";
			}
			// Log.
			$log->write_to_log("Converting segment".$t_c." using SQL JOIN...");
			// Create PDO object
			$this->db_connect();
			// Get.
			if($res = $this->pdo->query("INSERT INTO tbl_segment".$t_b."
									 (dq_flag_version_fk,
									  segment_start_time,
									  segment_stop_time,".$t_e."
									  PROCESS_ID,
									  SEGMENT_DEF_ID)
									 SELECT dq_flag_version_id, START_TIME, END_TIME, ".$t_d."SEGMENT".$t_a.".PROCESS_ID, SEGMENT".$t_a.".SEGMENT_DEF_ID
									 FROM tbl_dq_flag_versions
									 LEFT JOIN SEGMENT".$t_a." ON tbl_dq_flag_versions.SEGMENT_DEF_ID = SEGMENT".$t_a.".SEGMENT_DEF_ID")) {
												 // Log.
			$log->write_to_log("Finished converting segment".$t_c);
			}
			// Otherwise, output error.
			else {
				// Log.
				$log->write_to_log("ERROR - Problem converting segment".$t_c." - ".print_r($this->pdo->errorInfo()));
				// Set result to error to not automatically go on with segment summary insertion.
				$r = FALSE;
			}
		}
		// Log.
		$log->write_to_log("Finished converting segment".$t_c."s (version_id: ".$dq_flag_version_fk.", SEGMENT_DEF_ID: ".$SEGMENT_DEF_ID.") - ".$stmt->errorInfo[2]);
		// Return.
		return $r;
	}

/*	// Convert segments.
	private function convert_segments($s) {
		// Init.
		$r = TRUE;
		$t_a = NULL;
		$t_b = "s";
		$t_c = "s";
		$t_d = NULL;
		$t_e = NULL;
		// If dealing with summaries.
		if($s) {
			$t_a = "_SUMMARY";
			$t_b = "_summary";
			$t_c = " summaries";
			$t_d = "COMMENT,";
			$t_e = "version_uri,";
		}
		// Instantiate.
		$log = new Logger();
		// Log.
		$log->write_to_log("Converting segment".$t_c."...");
		// Create PDO object
		$this->db_connect();
		// Get.
		if($res = $this->pdo->query("INSERT INTO tbl_segment".$t_b."
									 (dq_flag_version_fk,
									  segment_start_time,
									  segment_stop_time,".$t_e."
									  PROCESS_ID,
									  SEGMENT_DEF_ID)
									 SELECT dq_flag_version_id, START_TIME, END_TIME, ".$t_d."SEGMENT".$t_a.".PROCESS_ID, SEGMENT".$t_a.".SEGMENT_DEF_ID
									 FROM tbl_dq_flag_versions
									 LEFT JOIN SEGMENT".$t_a." ON tbl_dq_flag_versions.SEGMENT_DEF_ID = SEGMENT".$t_a.".SEGMENT_DEF_ID")) {
			// Log.
			$log->write_to_log("Finished converting segment".$t_c);
		}
		// Otherwise, output error.
		else {
			// Log.
			$log->write_to_log("ERROR - Problem converting segment".$t_c." - ".print_r($this->pdo->errorInfo()));
			// Set result to error to not automatically go on with segment summary insertion.
			$r = FALSE;
		}
		// Return.
		return $r;
	}
*/}

?>