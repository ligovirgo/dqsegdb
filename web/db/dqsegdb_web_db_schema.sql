--
-- DQSEGDB Web Interface DB Creation SQL.
--

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Database: `dqsegdb_web`
--

-- --------------------------------------------------------

--
-- Table structure for table `tbl_contents`
--

CREATE TABLE IF NOT EXISTS `tbl_contents` (
  `content_id` int(5) unsigned zerofill NOT NULL AUTO_INCREMENT,
  `content_name` text CHARACTER SET utf8 NOT NULL,
  `content_parent` int(11) NOT NULL DEFAULT '0',
  `content_details` text CHARACTER SET utf8 NOT NULL,
  `content_uri` text NOT NULL,
  `content_inc_on_homepage_lx` int(11) NOT NULL DEFAULT '0',
  `content_inc_on_homepage_rx` int(11) NOT NULL DEFAULT '0',
  `content_inc_in_footer` int(11) NOT NULL DEFAULT '0',
  `content_hide_in_sitemap` int(11) NOT NULL DEFAULT '0',
  `content_hide_in_top_links` int(11) NOT NULL DEFAULT '0',
  `content_in_intranet` int(11) NOT NULL DEFAULT '0',
  `user_fk` int(11) NOT NULL DEFAULT '0',
  `date_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`content_id`),
  KEY `content_link` (`content_parent`),
  KEY `content_inc_in_footer` (`content_inc_in_footer`),
  KEY `content_inc_on_homepage` (`content_inc_on_homepage_rx`),
  KEY `user_fk` (`user_fk`),
  KEY `content_hide_in_sitemap` (`content_hide_in_sitemap`),
  KEY `content_hide_in_top_links` (`content_hide_in_top_links`),
  KEY `content_in_intranet` (`content_in_intranet`),
  KEY `content_inc_on_homepage_lx` (`content_inc_on_homepage_lx`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=35 ;

--
-- Dumping data for table `tbl_contents`
--

INSERT INTO `tbl_contents` (`content_id`, `content_name`, `content_parent`, `content_details`, `content_uri`, `content_inc_on_homepage_lx`, `content_inc_on_homepage_rx`, `content_inc_in_footer`, `content_hide_in_sitemap`, `content_hide_in_top_links`, `content_in_intranet`, `user_fk`, `date_updated`) VALUES
(00001, 'Home', 0, '', '', 0, 0, 0, 0, 0, 0, 9, '2015-04-15 07:37:47'),
(00002, 'Clients', 0, '<p>This section contains information relating to usage of the command-line and web-interface clients.</p>\r\n\r\n<ul>\r\n\r\n<li><a href="?c=3">Click here for information on the command-line clients.</a></li>\r\n\r\n<li><a href="?c=4">Click here for information on the web interface client.</a></li>\r\n\r\n</ul>', '', 0, 0, 0, 0, 0, 0, 9, '2015-04-15 07:37:47'),
(00003, 'Command-line', 2, '<p>\r\n        <strong>Git repo release</strong></p>\r\n<p>\r\n        # (Tested): Grab the releaseNov32014 branch of the dqsegdb git repo by doing the following:</p>\r\n<p>\r\n        # First, follow all the instructions on this page to set up your authentication: <a href="https://sugwg-git.phy.syr.edu/dokuwiki/doku.php" target="_blank">https://sugwg-git.phy.syr.edu/dokuwiki/doku.php</a> (this is because we have our git repo shibboleth protected)</p>\r\n<p>\r\n        # Checkout the dqsegdb repo (you need to do this every time you interact with the git repo):</p>\r\n<pre>\r\necp-cookie-init LIGO.ORG https://sugwg-git.phy.syr.edu/git/ albert.einstein</pre>\r\n<p>\r\n        # Get the package</p>\r\n<pre>\r\ngit clone https://sugwg-git.phy.syr.edu/git/dqsegdb</pre>\r\n<p>\r\n        # Change to the DQSEGDB directory.</p>\r\n<pre>\r\ncd dqsegdb</pre>\r\n<p>\r\n        # Checkout the release branch:</p>\r\n<pre>\r\ngit checkout releaseNov32014</pre>\r\n<p>\r\n        # Then, follow these instructions to install and use the new clients:</p>\r\n<p>\r\n        # &quot;Build&quot; the package, placing binaries and libraries into standard directories</p>\r\n<pre>\r\npython setup.py install --user</pre>\r\n<p>\r\n        # Setup your environment to look at the new directories. To do this: Follow instructions provided at end of previous command. For example:</p>\r\n<pre>\r\nsource /home/rfisher/.local/etc/dqsegdb-user-env.sh</pre>\r\n<p>\r\n        # This must be run each time you log in, or put it in your log in scripts (.bashrc).<br />\r\n        # This will install the code in your home directory and set up your paths to use it. Any time you want to use the clients, you just need to re-run the &quot;source ...&quot; line (or you can put it in your log in scripts).<br />\r\n        # Then, you can just use the new clients, pointing to the new server. Here is an example query. Note that in this example, we point to dqsegdb5:</p>\r\n<pre>\r\nligolw_segment_query_dqsegdb --segment-url=https://dqsegdb5.phy.syr.edu --query-segments\r\n--gps-start-time 1099033216 --gps-end-time 1099033316\r\n--include-segments=&quot;H1:ODC-PSL_SUMMARY:1&quot; -o example.xml</pre>', '', 0, 0, 0, 0, 0, 0, 9, '2015-04-15 07:37:47'),
(00004, 'Web interface', 2, '<h3>DQSEGDB hosts</h3>\r\n\r\n<p>It is possible to query diff DQSEGDB hosts via this web user interface (WUI). By default, the WUI connects to the host that responds quickest when the application is first opened. It continues to use this host until such time as the user tells it to do otherwise.</p>\r\n\r\n<p>The host currently in use is displayed at the top of the screen:</p>\r\n\r\n<img class="img_tutorial" src="images/tutorial/dqsegdb_wui_10_change_host.png" />\r\n\r\n<h4>Changing the host</h4>\r\n<p>To change the host, click on the ''Change this host'' option, to the right of the currently-in-use host.</p>\r\n\r\n<p>This converts the information into a select drop-down list, providing all of the currently available DQSEGDB hosts in the format ''URI (host dataset description)'':</p>\r\n\r\n<img class="img_tutorial" src="images/tutorial/dqsegdb_wui_11_changing_host.png" />\r\n\r\n<p>To change host, simply select the required host from the available list. The WUI will automatically update itself, based upon the information selected.</p>\r\n\r\n<h3>Retrieving segments</h3>\r\n\r\n<p>Querying DQSEGDB to retrieve segments via the WUI is straightforward once you get the hang of a few simple steps. This section explains what you need to know.</p>\r\n<p><N.B. In order for the WUI to function correctly, it is important to ensure JavaScript is activated in the browser.</p>\r\n\r\n<h4>Selecting the IFO</h4>\r\n\r\n<p>The WUI can be configured to look for flags relating to a single interferometer (IFO) or to look for flags associated to all IFO available in the database; it functions slightly differently, dependent upon which of these options are chosen.</p>\r\n\r\n<p>Choosing the ''Use all IFO'' option, results in all flags in the database being displayed in the Flags box, using an ''{IFO} - {FLAG_NAME}'' format:</p>\r\n\r\n<img class="img_tutorial" src="images/tutorial/dqsegdb_wui_1_all_ifo.png" />\r\n\r\n<p>In contrast, when a specific IFO has been chosen, the list of flags displayed in the Flag box simply provides the name of the flag:</p>\r\n\r\n<img class="img_tutorial" src="images/tutorial/dqsegdb_wui_2_specific_ifo.png" />\r\n\r\n<h4>Selecting the Flags</h4>\r\n<p>Two options are available to users when selecting the Flags to include in the query to the DQSEGDB server: individual selection; and copy/paste.</p>\r\n\r\n<h5>Individual selection</h5>\r\n\r\n<p>Users can individually select flags from the list available in the Flags select box. By holding down the CTRL key, is possible to accumulate multiple flags together into the same request. Once the user releases the left-mouse button, the selected flags are automatically passed to the Versions element of the Query form and listed along with their available associated versions:</p>\r\n\r\n<img class="img_tutorial" src="images/tutorial/dqsegdb_wui_3_flags_selected.png" />\r\n\r\n<h5>Copy/Paste</h5>\r\n\r\n<p>By clicking on the ''Change Flag-selection option'' link, users can alter the way in which they choose the flags to include in the query. This is because it may simply be too arduous a process to identify multiple required flags among the list of those available.</p>\r\n<p>Clicking on the ''Change Flag-selection option'' link alters the Query form to the following:</p>\r\n\r\n<img class="img_tutorial" src="images/tutorial/dqsegdb_wui_5_copy_paste.png" />\r\n\r\n<p>Flag names can be typed or copied and pasted directly into this Flag box as a list.</p>\r\n\r\n<p>However, once again, it is necessary to take into account the way in which the IFO has been selected earlier in the form. In the event of a specific IFO having been selected, the flags can be entered using the following format:</p>\r\n\r\n<img class="img_tutorial" src="images/tutorial/dqsegdb_wui_6_flags_pasted.png" />\r\n\r\n<p>Instead, if the ''Use all IFO'' option has been selected, it is necessary to include the IFO associated to the flag in the same line, using the ''{IFO} - {FLAG_NAME}'' format. For example</p>\r\n\r\n<img class="img_tutorial" src="images/tutorial/dqsegdb_wui_12_flags_pasted_all_ifo.png" />\r\n<h4>Selecting the Versions</h4>\r\n\r\n<p>Once the flags have been chosen, it is necessary to choose the required versions. To do so, simply click on the required versions among those listed to the right of the flag name in the Versions section. Once selected, a the white background of the version disappears:</p>\r\n\r\n<img class="img_tutorial" src="images/tutorial/dqsegdb_wui_4_versions_selected.png" />\r\n\r\n<p>Note that a selected version can be de-selected by clicking on it once again.</p>\r\n\r\n<h4>Sending the Request</h4>\r\n\r\n<p>Once the required version(s) has/have been selected, it is possible to send the request to the DQSEGDB Server. To do so, click on the ''Retrieve Segments'' button. The button then alters to an ''in-operation'' graphic, until the results have been served and returned:</p>\r\n<img class="img_tutorial" src="images/tutorial/dqsegdb_wui_7_retrieving_segments.png" />\r\n\r\n<h5>GPS time filtering</h5>\r\n\r\n<p>By default, any requests to the DQSEGDB Server will return all segments associated to the requested flag versions. However, these can also be filtered by earliest GPS Start and End times, by using the dedicated input options in the Query form.</p>\r\n\r\n<h3>Viewing recent requests</h3>\r\n\r\n<p>When a request to the DQSEGDB Server from the WUI completes, the resulting JSON payload is written to a file and stored for use when required. The most-recently-created JSON payloads are made available in the ''Recent Query Results'' section:</p>\r\n\r\n<img class="img_tutorial" src="images/tutorial/dqsegdb_wui_8_recent_queries.png" />\r\n\r\n<p>This section provides the following information relating to a saved payload:</p>\r\n<ul>\r\n<li>the date and time on which the request was made;</li>\r\n<li>the dataset to which the request relates;</li>\r\n<li>the URI sent during the request;</li>\r\n<li>and the size of the resultant JSON payload, displayed in either KB or MB, dependant upon the size of the reply returned.</li>\r\n</ul>\r\n\r\n<h3>Accessing retrieved segments</h3>\r\n\r\n<p>Clicking on one of the URI in the ''Recent Query Results'' section automatically opens the JSON payload in another browser tab. Alternatively, right-clicking on the URI should provide the option to download the file. The JSON payload will look something similar to the following:</p>\r\n\r\n<img class="img_tutorial" src="images/tutorial/dqsegdb_wui_9_json_payload.png" />', '', 0, 0, 0, 0, 0, 0, 9, '2015-04-15 07:37:47'),
(00008, 'Monitoring', 0, '<p>This section contains information that may be useful in monitoring the status of the various DQSEGDB-related host machines.</p>\r\n\r\n<p>The following information is currently available:</p>\r\n\r\n<ul>\r\n<li><a href="?c=34">Database statistics</a> - information relating to the number of flags, versions and segments available; and earliest and latest segment start and stop times, on each of the DQSEGDB hosts. Information is also broken down to individual interferometer level.</li>\r\n<li><a href="?c=29">Logs</a> - The DQSEGDB server log file for the web interface host.</li>\r\n</ul>', '', 0, 0, 0, 0, 0, 0, 9, '2015-04-15 07:37:47'),
(00013, 'Documentation', 0, '', 'https://tds.ego-gw.it/ql/?s=2334', 0, 0, 0, 0, 0, 0, 9, '2015-04-15 07:37:47'),
(00014, 'User Requirements', 13, '', 'https://tds.ego-gw.it/ql/?c=9366', 0, 0, 0, 0, 0, 0, 9, '2015-04-15 07:37:47'),
(00015, 'Database Structure', 13, '', 'https://tds.ego-gw.it/ql/?c=9774', 0, 0, 0, 0, 0, 0, 9, '2015-04-15 07:37:47'),
(00017, 'Sitemap', 1, '', '', 0, 0, 1, 0, 0, 0, 9, '2015-04-15 07:37:47'),
(00020, 'API Specification', 13, '', 'https://tds.ego-gw.it/ql/?c=9693', 0, 0, 0, 0, 0, 0, 9, '2015-04-15 07:37:47'),
(00022, 'Available resources', 5, '', '', 0, 1, 0, 0, 1, 0, 9, '2015-04-15 07:37:47'),
(00024, 'Query DQSEGDB', 1, '<p>Use this form to get segments from DQSEGDB</p>', '', 1, 0, 0, 0, 0, 0, 9, '2015-04-15 07:37:47'),
(00025, 'Presentations', 13, '', 'https://tds.ego-gw.it/ql/?s=2334', 0, 0, 0, 0, 0, 0, 9, '2015-04-15 07:37:47'),
(00026, 'DQSEGDB details', 1, '', '', 0, 1, 0, 0, 0, 0, 9, '2015-04-15 07:37:47'),
(00027, 'Recent query results', 1, '', '', 1, 0, 0, 0, 0, 0, 9, '2015-04-15 07:37:47'),
(00029, 'Logs', 8, '', '', 0, 0, 0, 0, 0, 0, 9, '2015-04-15 07:37:47'),
(00030, 'DQSEGDB current status', 1, '<p>The DQSEGDB instances are currently in the following states:</p>', '', 1, 0, 0, 0, 0, 0, 9, '2015-04-15 07:37:47'),
(00034, 'Database statistics', 8, '', '', 0, 0, 0, 0, 0, 0, 9, '2015-04-15 07:37:47');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_file_metadata`
--

CREATE TABLE IF NOT EXISTS `tbl_file_metadata` (
  `file_id` int(11) NOT NULL AUTO_INCREMENT,
  `file_name` text NOT NULL,
  `file_size` int(11) NOT NULL DEFAULT '0',
  `file_uri_used` text NOT NULL,
  `user_fk` int(11) NOT NULL DEFAULT '0',
  `file_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `host_fk` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`file_id`),
  KEY `file_size` (`file_size`,`user_fk`),
  KEY `host_fk` (`host_fk`),
  KEY `user_fk` (`user_fk`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_values`
--

CREATE TABLE IF NOT EXISTS `tbl_values` (
  `value_id` int(11) NOT NULL AUTO_INCREMENT,
  `value_group_fk` int(11) NOT NULL DEFAULT '0',
  `value_txt` text NOT NULL,
  `value_add_info` text NOT NULL,
  PRIMARY KEY (`value_id`),
  KEY `value_group_fk` (`value_group_fk`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=10 ;

--
-- Dumping data for table `tbl_values`
--

INSERT INTO `tbl_values` (`value_id`, `value_group_fk`, `value_txt`, `value_add_info`) VALUES
(0, 1, 'No', ''),
(1, 1, 'Yes', ''),
(5, 2, 'http://dqsegdb4.phy.syr.edu', 'S6'),
(6, 2, 'http://dqsegdb7.phy.syr.edu', 'GEO'),
(7, 2, 'http://dqsegdb6.phy.syr.edu', 'TEST'),
(8, 2, 'http://10.20.5.42', 'dqsegdb3 - PRODUCTION COPY'),
(9, 3, 'gary.hemming', '');

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
(1, 'Yes/No'),
(2, 'Hosts'),
(3, 'Users');

--
-- Constraints for dumped tables
--

--
-- Constraints for table `tbl_contents`
--
ALTER TABLE `tbl_contents`
  ADD CONSTRAINT `tbl_contents_ibfk_1` FOREIGN KEY (`user_fk`) REFERENCES `tbl_values` (`value_id`);

--
-- Constraints for table `tbl_file_metadata`
--
ALTER TABLE `tbl_file_metadata`
  ADD CONSTRAINT `tbl_file_metadata_ibfk_2` FOREIGN KEY (`host_fk`) REFERENCES `tbl_values` (`value_id`),
  ADD CONSTRAINT `tbl_file_metadata_ibfk_1` FOREIGN KEY (`user_fk`) REFERENCES `tbl_values` (`value_id`);
