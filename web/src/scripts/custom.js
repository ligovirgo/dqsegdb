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
			// Show retrieve segment button.
			$("#divForsubmit_segment_form").css("visibility", "visible");
			// Re-write form.
			$('#div_version_div').html(r);
		}
	});
}

// Update the flag version div using contents of textarea.
function update_div_flag_versions_from_ta() {
	// Get currently selected IFO.
	var dq_flag = $("#ta_dq_flag").val().replace(/\n/g, "[[[BREAK]]]");
	// Update version div.
	$.get("scripts/actions.php?ad_type=update_version_div_from_ta&dq_flag=" + dq_flag, function(r) {
		// If result retrieved
		if(r != 0) {
			// Show retrieve segment button.
			$("#divForsubmit_segment_form").css("visibility", "visible");
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


// Retrieve segments.
function retrieve_segments() {
	// Get GPS start and stop times.
	s = $("#gps_start_time").val();
	e = $("#gps_stop_time").val();
	// Hide button and show message.
	$("#divForsubmit_segment_form").fadeOut('fast');
	$("#img_retrieval_msg").fadeIn('fast');
	$("#img_retrieval_msg").css("visibility", "visible");
	// Update version div.
	$.get("scripts/actions.php?ad_type=retrieve_segments&s=" + s + "&e=" + e, function(r) {
		// If result retrieved
		if(r != 0) {
			alert(r);
		}
		// Show button and hide message.
//		$("#divForsubmit_segment_form").css("visibility", "visible");
		$("#divForsubmit_segment_form").fadeIn('fast');
		$("#img_retrieval_msg").fadeOut('fast');
		$("#img_retrieval_msg").css("visibility", "hidden");
		// Re-build the Recent Query Results list.
		rebuild_recent_query_results_list();
	});
}

// Re-build the Recent Query Results list.
function rebuild_recent_query_results_list() {
	// Update version div.
	$.get("scripts/actions.php?ad_type=get_recent_query_results", function(r) {
		// If results retrieved.
		if(r != 0) {
			$('#div_recent_query_results').html(r);
		}
	});
}

// De-/Activate the drop-down select for use in host changing.
function activate_host_change_option() {
	// Get current host box.
	$.get("scripts/actions.php?ad_type=get_current_host_box", function(r) {
		// If results retrieved.
		if(r != 0) {
			// Re-build contents.
			$('#div_current_host').html(r);
			// Hide 'Change this host' message.
			$("#span_change_host").css("visibility", "hidden");
		}
	});
}

// Update the host in use.
function update_host() {
	// Init.
	h = $('#sel_change_host').find(":selected").val();
	// Get current host box.
	$.get("scripts/actions.php?ad_type=set_current_host&h=" + h, function() {
		// Reload page.
		location.reload();
	});
}

// Alternate the available flag_choice option.
function alternate_flag_option() {
	// Alternate flag choice option.
	$.get("scripts/actions.php?ad_type=alternate_flag_choice_option", function(r) {
		// If result returned.
		if(r != 0) {
			$('#input_Flags_val').html(r);
		}
	});
}