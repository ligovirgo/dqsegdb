-- phpMyAdmin SQL Dump
-- version 3.4.3.2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: May 16, 2016 at 12:20 AM
-- Server version: 5.1.73
-- PHP Version: 5.3.3

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `dqsegdb`
--

-- --------------------------------------------------------

--
-- Table structure for table `tbl_dq_flags`
--

CREATE TABLE IF NOT EXISTS `tbl_dq_flags` (
  `dq_flag_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Individual unique identifier. Required for internal DB relationships.',
  `dq_flag_name` text NOT NULL COMMENT 'Text string descriptive flag name.',
  `dq_flag_ifo` int(11) NOT NULL DEFAULT '0' COMMENT 'Related interferometer. Foreign Key linked to tbl_values.',
  `dq_flag_assoc_versions` text NOT NULL COMMENT 'Comma-delimited list of versions associated to this Flag.',
  `dq_flag_active_means_ifo_badness` tinyint(1) DEFAULT NULL COMMENT '1 if the flag being active means the IFO is in a ‘bad’ state. NULL if unknown or not applicable.',
  `dq_flag_creator` int(11) DEFAULT NULL COMMENT 'User that created flag. Foreign Key linked to tbl_values.',
  `dq_flag_date_created` double NOT NULL COMMENT 'GPS time of flag creation.',
  PRIMARY KEY (`dq_flag_id`),
  KEY `dq_flag_active_means_ifo_badness` (`dq_flag_active_means_ifo_badness`),
  KEY `dq_flag_ifo` (`dq_flag_ifo`),
  KEY `dq_flag_creator` (`dq_flag_creator`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 COMMENT='Contains metadata relating to the individual flags.' AUTO_INCREMENT=1090 ;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_dq_flag_versions`
--

CREATE TABLE IF NOT EXISTS `tbl_dq_flag_versions` (
  `dq_flag_version_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary Key. Individual unique identifier. Required for internal DB relationships.',
  `dq_flag_fk` int(11) NOT NULL DEFAULT '0' COMMENT 'Foreign Key linked to flag.',
  `dq_flag_description` text NOT NULL COMMENT 'String description of why flag was created.',
  `dq_flag_version` int(11) NOT NULL DEFAULT '0' COMMENT 'Individual incrementing version number.',
  `dq_flag_version_known_segment_total` int(11) NOT NULL DEFAULT '0' COMMENT 'Total number of known segments associated to a version.',
  `dq_flag_version_known_earliest_segment_time` double NOT NULL COMMENT 'Time of first known segment start time associated to this version.',
  `dq_flag_version_known_latest_segment_time` double NOT NULL COMMENT 'Time of last known segment stop time associated to this version.',
  `dq_flag_version_active_segment_total` int(11) NOT NULL DEFAULT '0' COMMENT 'Total number of active segments associated to a version.',
  `dq_flag_version_active_earliest_segment_time` double NOT NULL COMMENT 'Time of first active segment start time associated to this version.',
  `dq_flag_version_active_latest_segment_time` double NOT NULL COMMENT 'Time of last active segment stop time associated to this version.',
  `dq_flag_version_deactivated` int(1) NOT NULL DEFAULT '0' COMMENT 'Is this version unavailable?',
  `dq_flag_version_comment` text NOT NULL COMMENT 'Short text comment about version.',
  `dq_flag_version_uri` text NOT NULL COMMENT 'URI to further externally- stored information relating to version.',
  `dq_flag_version_last_modifier` int(11) NOT NULL DEFAULT '0' COMMENT 'Foreign Key. User ID of last user to have modified version with appended segments.',
  `dq_flag_version_date_created` double NOT NULL COMMENT 'GPS time of version creation.',
  `dq_flag_version_date_last_modified` double NOT NULL COMMENT 'GPS time of most-recent version modification with segment append.',
  PRIMARY KEY (`dq_flag_version_id`),
  KEY `dq_flag_version_creator` (`dq_flag_version`),
  KEY `dq_flag_fk` (`dq_flag_fk`),
  KEY `dq_flag_versio_unavailable` (`dq_flag_version_deactivated`),
  KEY `dq_flag_version_last_modifier` (`dq_flag_version_last_modifier`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 COMMENT='Contains metadata related to the individual flag versions.' AUTO_INCREMENT=1124 ;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_processes`
--

CREATE TABLE IF NOT EXISTS `tbl_processes` (
  `process_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary Key. Individual unique\nidentifier. Required for internal DB relationships.',
  `dq_flag_version_fk` int(11) NOT NULL DEFAULT '0' COMMENT 'Foreign Key linked to flag-version ID.',
  `process_full_name` text NOT NULL COMMENT 'Full name of launching process.',
  `pid` int(11) NOT NULL DEFAULT '0' COMMENT 'System ID of launching process.',
  `fqdn` text NOT NULL COMMENT 'Fully Qualified Domain name of machine on which process was launched.',
  `process_args` text NOT NULL,
  `process_comment` text NOT NULL,
  `user_fk` int(11) NOT NULL DEFAULT '0' COMMENT 'Foreign Key linked to tbl_users.',
  `insertion_time` double NOT NULL COMMENT 'GPS time of row insertion.',
  `affected_active_data_segment_total` int(11) NOT NULL DEFAULT '0' COMMENT 'Number of active segments uploaded by this process.',
  `affected_active_data_start` double NOT NULL DEFAULT '0' COMMENT 'GPS start time of earliest active segment associated to this process.',
  `affected_active_data_stop` double NOT NULL DEFAULT '0' COMMENT 'GPS stop time of latest active segment associated to this process.',
  `affected_known_data_segment_total` int(11) NOT NULL DEFAULT '0' COMMENT 'Number of known segments uploaded by this process.',
  `affected_known_data_start` double NOT NULL DEFAULT '0' COMMENT 'GPS start time of earliest known segment associated to this process.',
  `affected_known_data_stop` double NOT NULL DEFAULT '0' COMMENT 'GPS stop time of latest known segment associated to this process.',
  `process_time_started` double NOT NULL COMMENT 'GPS time process started.',
  `process_time_last_used` double NOT NULL COMMENT 'GPS time process last used.',
  PRIMARY KEY (`process_id`),
  KEY `dq_flag_version_fk` (`dq_flag_version_fk`),
  KEY `user_fk` (`user_fk`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=23368508 ;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_segments`
--

CREATE TABLE IF NOT EXISTS `tbl_segments` (
  `dq_flag_version_fk` int(11) NOT NULL COMMENT 'Foreign Key linked to flag version ID.',
  `segment_start_time` double NOT NULL COMMENT 'Segment start GPS time.',
  `segment_stop_time` double NOT NULL COMMENT 'Segment stop GPS time.',
  KEY `dq_flag_version_fk` (`dq_flag_version_fk`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Contains all segments classified as ‘Known & Active’.';

-- --------------------------------------------------------

--
-- Table structure for table `tbl_segment_summary`
--

CREATE TABLE IF NOT EXISTS `tbl_segment_summary` (
  `dq_flag_version_fk` int(11) NOT NULL DEFAULT '0' COMMENT 'Foreign Key linked to flag version ID.',
  `segment_start_time` double NOT NULL COMMENT 'Segment start GPS time.',
  `segment_stop_time` double NOT NULL COMMENT 'Segment stop GPS time.',
  KEY `dq_flag_version_fk` (`dq_flag_version_fk`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Contains all segments classified as ‘Known’.';

-- --------------------------------------------------------

--
-- Table structure for table `tbl_values`
--

CREATE TABLE IF NOT EXISTS `tbl_values` (
  `value_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary Key. Individual unique identifier. Required for internal DB relationships.',
  `value_group_fk` int(11) NOT NULL DEFAULT '0' COMMENT 'Foreign Key. Linked to tbl_value_groups.',
  `value_txt` text NOT NULL COMMENT 'Text string.',
  PRIMARY KEY (`value_id`),
  KEY `value_group_fk` (`value_group_fk`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 COMMENT='Contains internal application metadata.' AUTO_INCREMENT=21 ;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_value_groups`
--

CREATE TABLE IF NOT EXISTS `tbl_value_groups` (
  `value_group_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Individual unique identifier. Required for internal DB relationships.',
  `value_group` text NOT NULL COMMENT 'Text string.',
  PRIMARY KEY (`value_group_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 COMMENT='Contain internal application value-group metadata.' AUTO_INCREMENT=4 ;

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

--
-- Data for dumped tables
--

--
-- Dumping data for table `tbl_value_groups`
--

INSERT INTO `tbl_value_groups` (`value_group_id`, `value_group`) VALUES
(1, 'IFO'),
(2, 'User'),
(3, 'Data format');

--
-- Dumping data for table `tbl_values`
--

INSERT INTO `tbl_values` (`value_id`, `value_group_fk`, `value_txt`) VALUES
(1, 1, 'V1'),
(2, 1, 'H1'),
(3, 1, 'L1'),
(4, 3, 'ASCII'),
(5, 3, 'LIGOLW XML');

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
