mv cats_test_output cats_test_output_$(date +"%Y%m%d")
mkdir cats_test_output
ligolw_segments_from_cats_dqsegdb --separate-categories --individual-results --segment-url https://segments-s6.ligo.org --veto-file H1L1V1-S6_CBC_HIGHMASS_D_OFFLINE-961545543-0.xml -s 931035615 -e 971654415 -o cats_test_output
