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
mv cats_test_output cats_test_output_$(date +"%Y%m%d")
mkdir cats_test_output
ligolw_segments_from_cats_dqsegdb --separate-categories --individual-results --segment-url https://segments-s6.ligo.org --veto-file H1L1V1-S6_CBC_HIGHMASS_D_OFFLINE-961545543-0.xml -s 931035615 -e 971654415 -o cats_test_output
