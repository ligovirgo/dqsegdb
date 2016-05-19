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
