/* === Custom JavaScripts === */

// Update the query server div.
function update_div_query_server() {
	// Get currently selected IFO.
	var ifo = $("#ifo").val();
	// Init.
	r = 0;
	// Update.
	$.get("scripts/actions.php?ad_type=update_div_query_server&ifo=" +  ifo, function(r) {
		// If result retrieved
		if(r != 0) {
			// Re-write form.
			$('#div_query_server').html(r);
		}
	});
}

// Update the flag version div.
function update_div_flag_versions() {
	// Get currently selected IFO.
	var dq_flag = $("#dq_flag").val();
	// Init.
	r = 0;
	// Update version div.
	$.get("scripts/actions.php?ad_type=update_version_div&dq_flag=" + dq_flag, function(r) {
		// If result retrieved
		if(r != 0) {
			// Re-write form.
			$('#div_version_div').html(r);
		}
	});
}

// Select/De-select a specific flag version URI.
function deselect_version_uri(span_name, uri) {
	// Init.
	r = 0;
	// Update version div.
	$.get("scripts/actions.php?ad_type=deselect_version_uri&uri=" + uri, function(r) {
		// If result retrieved
		if(r != 0) {
			// Re-write form.
			$('#' + span_name).attr('class', r).fadeIn('slow');
		}
	});
}