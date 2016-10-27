echo "Usage:  takes in a suffix to append to the default flag name.  Inserts a flag using this suffix'd name, then queries that flag.  You should see active segments in the output."
suffix=$1
ligolw_segment_insert_dqsegdb --segment-url https://segments-dev.ligo.org --ifos H1 --name DCH-TEST_RYAN_${suffix} --version=1 --comment "Testing Segment Insertions for SL7" --explain ""Testing Segment Insertions for SL7"" --segment-file=H1_TEST_2.txt --summary-file=H1_TEST_2_SUMMARY.txt --insert
ligolw_segment_query_dqsegdb --segment-url=https://segments-dev.ligo.org --query-segments --gps-start-time 1000000000  --gps-end-time 1000000140 --include-segments="H1:DCH-TEST_RYAN_${suffix}:1"
