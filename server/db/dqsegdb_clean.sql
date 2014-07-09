--
-- Table structure for table `tbl_dq_flags`
--

CREATE TABLE IF NOT EXISTS `tbl_dq_flags` (
  `dq_flag_id` int(11) NOT NULL AUTO_INCREMENT,
  `dq_flag_name` text NOT NULL,
  `dq_flag_description` text NOT NULL,
  `dq_flag_ifo` int(11) NOT NULL DEFAULT '0',
  `dq_flag_assoc_versions` text NOT NULL COMMENT 'Comma-delimited list of associated versions.',
  `dq_flag_active_means_ifo_badness` tinyint(1) DEFAULT NULL,
  `dq_flag_creator` int(11) DEFAULT NULL,
  `dq_flag_date_created` double NOT NULL,
  PRIMARY KEY (`dq_flag_id`),
  KEY `dq_flag_active_means_ifo_badness` (`dq_flag_active_means_ifo_badness`),
  KEY `dq_flag_ifo` (`dq_flag_ifo`),
  KEY `dq_flag_creator` (`dq_flag_creator`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_dq_flag_versions`
--

CREATE TABLE IF NOT EXISTS `tbl_dq_flag_versions` (
  `dq_flag_version_id` int(11) NOT NULL AUTO_INCREMENT,
  `dq_flag_fk` int(11) NOT NULL DEFAULT '0',
  `dq_flag_version` int(11) NOT NULL DEFAULT '0',
  `dq_flag_version_segment_total` int(11) NOT NULL DEFAULT '0',
  `dq_flag_version_earliest_segment_time` double NOT NULL DEFAULT '0',
  `dq_flag_version_latest_segment_time` double NOT NULL DEFAULT '0',
  `dq_flag_version_deactivated` int(1) NOT NULL DEFAULT '0' COMMENT 'Is\r\nthis version unavailable?',
  `dq_flag_version_description` text NOT NULL,
  `dq_flag_version_uri` text NOT NULL,
  `dq_flag_version_last_modifier` int(11) NOT NULL DEFAULT '0',
  `dq_flag_version_date_created` double NOT NULL,
  `dq_flag_version_date_last_modified` double NOT NULL,
  PRIMARY KEY (`dq_flag_version_id`),
  KEY `dq_flag_version_creator` (`dq_flag_version`),
  KEY `dq_flag_fk` (`dq_flag_fk`),
  KEY `dq_flag_versio_unavailable` (`dq_flag_version_deactivated`),
  KEY `dq_flag_version_last_modifier` (`dq_flag_version_last_modifier`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_processes`
--

CREATE TABLE IF NOT EXISTS `tbl_processes` (
  `process_id` int(11) NOT NULL AUTO_INCREMENT,
  `dq_flag_version_fk` int(11) NOT NULL DEFAULT '0',
  `process_full_name` text NOT NULL,
  `pid` int(11) NOT NULL DEFAULT '0',
  `fqdn` text NOT NULL,
  `data_format_fk` int(11) NOT NULL DEFAULT '0',
  `user_fk` int(11) NOT NULL DEFAULT '0',
  `insertion_time` double NOT NULL,
  `affected_data_segment_total` double NOT NULL,
  `affected_data_start` double NOT NULL,
  `affected_data_stop` double NOT NULL,
  `process_time_started` double NOT NULL,
  `process_time_last_used` double NOT NULL DEFAULT '0',
  PRIMARY KEY (`process_id`),
  KEY `user_fk` (`user_fk`),
  KEY `pid` (`pid`),
  KEY `upload_format_fk` (`data_format_fk`),
  KEY `dq_flag_version_fk` (`dq_flag_version_fk`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 ROW_FORMAT=COMPACT AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_process_args`
--

CREATE TABLE IF NOT EXISTS `tbl_process_args` (
  `process_arg_id` int(11) NOT NULL AUTO_INCREMENT,
  `process_fk` int(11) NOT NULL DEFAULT '0',
  `process_argv` text NOT NULL,
  PRIMARY KEY (`process_arg_id`),
  KEY `process_fk` (`process_fk`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Arguments passed by the process' AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_segments`
--

CREATE TABLE IF NOT EXISTS `tbl_segments` (
  `dq_flag_version_fk` int(11) NOT NULL,
  `segment_start_time` double NOT NULL,
  `segment_stop_time` double NOT NULL,
  KEY `dq_flag_version_fk` (`dq_flag_version_fk`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_segment_summary`
--

CREATE TABLE IF NOT EXISTS `tbl_segment_summary` (
  `dq_flag_version_fk` int(11) NOT NULL DEFAULT '0',
  `segment_start_time` double NOT NULL,
  `segment_stop_time` double NOT NULL,
  KEY `dq_flag_version_fk` (`dq_flag_version_fk`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_values`
--

CREATE TABLE IF NOT EXISTS `tbl_values` (
  `value_id` int(11) NOT NULL AUTO_INCREMENT,
  `value_group_fk` int(11) NOT NULL DEFAULT '0',
  `value_txt` text NOT NULL,
  PRIMARY KEY (`value_id`),
  KEY `value_group_fk` (`value_group_fk`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=6 ;

--
-- Dumping data for table `tbl_values`
--

INSERT INTO `tbl_values` (`value_id`, `value_group_fk`, `value_txt`) VALUES
(1, 1, 'V1'),
(2, 1, 'H1'),
(3, 1, 'L1'),
(4, 3, 'ASCII'),
(5, 3, 'LIGOLW XML');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_value_groups`
--

CREATE TABLE IF NOT EXISTS `tbl_value_groups` (
  `value_group_id` int(11) NOT NULL AUTO_INCREMENT,
  `value_group` text NOT NULL,
  PRIMARY KEY (`value_group_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=4 ;

--
-- Dumping data for table `tbl_value_groups`
--

INSERT INTO `tbl_value_groups` (`value_group_id`, `value_group`) VALUES
(1, 'IFO'),
(2, 'User'),
(3, 'Data format');

--
-- Constraints for dumped tables
--

--
-- Constraints for table `tbl_dq_flags`
--
ALTER TABLE `tbl_dq_flags`
  ADD CONSTRAINT `tbl_dq_flags_ibfk_1` FOREIGN KEY (`dq_flag_ifo`) REFERENCES `tbl_values` (`value_id`),
  ADD CONSTRAINT `tbl_dq_flags_ibfk_2` FOREIGN KEY (`dq_flag_creator`) REFERENCES `tbl_values` (`value_id`);

--
-- Constraints for table `tbl_dq_flag_versions`
--
ALTER TABLE `tbl_dq_flag_versions`
  ADD CONSTRAINT `tbl_dq_flag_versions_ibfk_2` FOREIGN KEY (`dq_flag_version_last_modifier`) REFERENCES `tbl_values` (`value_id`),
  ADD CONSTRAINT `tbl_dq_flag_versions_ibfk_3` FOREIGN KEY (`dq_flag_fk`) REFERENCES `tbl_dq_flags` (`dq_flag_id`);

--
-- Constraints for table `tbl_processes`
--
ALTER TABLE `tbl_processes`
  ADD CONSTRAINT `tbl_processes_ibfk_2` FOREIGN KEY (`data_format_fk`) REFERENCES `tbl_values` (`value_id`),
  ADD CONSTRAINT `tbl_processes_ibfk_3` FOREIGN KEY (`user_fk`) REFERENCES `tbl_values` (`value_id`),
  ADD CONSTRAINT `tbl_processes_ibfk_4` FOREIGN KEY (`dq_flag_version_fk`) REFERENCES `tbl_dq_flag_versions` (`dq_flag_version_id`);

--
-- Constraints for table `tbl_process_args`
--
ALTER TABLE `tbl_process_args`
  ADD CONSTRAINT `tbl_process_args_ibfk_1` FOREIGN KEY (`process_fk`) REFERENCES `tbl_processes` (`process_id`);

--
-- Constraints for table `tbl_segments`
--
ALTER TABLE `tbl_segments`
  ADD CONSTRAINT `tbl_segments_ibfk_1` FOREIGN KEY (`dq_flag_version_fk`) REFERENCES `tbl_dq_flag_versions` (`dq_flag_version_id`);

--
-- Constraints for table `tbl_segment_summary`
--
ALTER TABLE `tbl_segment_summary`
  ADD CONSTRAINT `tbl_segment_summary_ibfk_1` FOREIGN KEY (`dq_flag_version_fk`) REFERENCES `tbl_dq_flag_versions` (`dq_flag_version_id`);

--
-- Constraints for table `tbl_values`
--
ALTER TABLE `tbl_values`
  ADD CONSTRAINT `tbl_values_ibfk_1` FOREIGN KEY (`value_group_fk`) REFERENCES `tbl_value_groups` (`value_group_id`);

