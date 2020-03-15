# Copyright (C) 2014-2020 Syracuse University, European Gravitational Observatory, and Christopher Newport University.  Written by Ryan Fisher and Gary Hemming. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
echo "Usage:  takes in a suffix to append to the default flag name.  Inserts a flag using this suffix'd name, then queries that flag.  You should see active segments in the output."
suffix=$1
ligolw_segment_insert_dqsegdb --segment-url https://segments-dev.ligo.org --ifos H1 --name DCH-TEST_RYAN_${suffix} --version=1 --comment "Testing Segment Insertions for SL7" --explain ""Testing Segment Insertions for SL7"" --segment-file=H1_TEST_2.txt --summary-file=H1_TEST_2_SUMMARY.txt --insert
ligolw_segment_query_dqsegdb --segment-url=https://segments-dev.ligo.org --query-segments --gps-start-time 1000000000  --gps-end-time 1000000140 --include-segments="H1:DCH-TEST_RYAN_${suffix}:1"
