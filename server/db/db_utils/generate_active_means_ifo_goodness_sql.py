# Copyright (C) 2014-2020 Syracuse University, European Gravitational Observatory, and Christopher Newport University.  Written by Ryan Fisher and Gary Hemming. See the NOTICE file distributed with this work for additional information regarding copyright ownership.

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
blah=open('active_means_ifo_goodness_list_hand_edited.txt','r')
listintxt=blah.readlines()
blah.close()

ifodict={}
ifodict['H1']=2
ifodict['L1']=3

blah2=open('set_flags_active_means_goodness.sql','w')
for i in listintxt:
  ifonum=ifodict[i.strip().split('/')[0]]
  name=i.strip().split('/')[1]
  txtout="""UPDATE tbl_dq_flags SET dq_flag_active_means_ifo_badness=0 WHERE dq_flag_name LIKE '%s' and dq_flag_ifo=%d;""" % (name,ifonum)
  blah2.writelines(txtout)
blah2.close()
