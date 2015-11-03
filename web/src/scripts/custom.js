/* === Custom JavaScripts === */

// Update the query server div.
function update_div_query_server() {
	// Get currently selected IFO.
	var ifo = $("#ifo").val();
	// Init.
	r = 0;
	// Update.
	$.get("scripts/actions.php?req=update_div_query_server&ifo=" +  ifo, function(r) {
		// If result retrieved
		if(r != 0) {
			// Re-write form.
			$('#div_query_server').html(r);
		}
	});
}

// Update the flag version div.
function update_div_flag_versions(max) {
	// Get currently selected flag.
	var dq_flag = $("#dq_flag").val();
	// If number of elements in list is less than or equal to 10.
	if(dq_flag.length <= 10) {
		// Init.
		r = 0;
		// Update version div.
		$.get("scripts/actions.php?req=update_version_div&dq_flag=" + dq_flag, function(r) {
			// If result retrieved
			if(r != 0) {
				// Show retrieve segment button.
				$("#divForsubmit_segment_form").css("visibility", "visible");
				// Re-write form.
				$('#div_version_div').html(r);
			}
		});
	}
	// Otherwise, if number of elements in list is more than 10.
	else {
		alert(get_too_many_flags_msg(dq_flag.length, max));
	}
}

// Update the flag version div using contents of textarea.
function update_div_flag_versions_from_ta(max) {
	// Set flag string.
	var f_string = "[\"" + $("#ta_dq_flag").val().replace(/\n/g, "\",\"") + "\"]";
	// Get currently selected IFO.
	var dq_flag_list = JSON.parse(f_string);
	// If number of elements in list is less than or equal to 10.
	if(dq_flag_list.length <= 10) {
		var dq_flag = $("#ta_dq_flag").val().replace(/\n/g, "[[[BREAK]]]");
		// Update version div.
		$.get("scripts/actions.php?req=update_version_div_from_ta&dq_flag=" + dq_flag, function(r) {
			// If result retrieved
			if(r != 0) {
				// Show retrieve segment button.
				$("#divForsubmit_segment_form").css("visibility", "visible");
				// Re-write form.
				$('#div_version_div').html(r);
			}
		});
	}
	// Otherwise, if number of elements in list is more than 10.
	else {
		alert(get_too_many_flags_msg(dq_flag_list.length, max));
	}
}

function get_too_many_flags_msg(len, max) {
	// Init.
	r = '';
	// Set.
	r = len + ' flags have currently been selected.\n\nThe maximum allowable limit via this interface is ' + max;
	// Return.
	return r;
}

// Select/De-select a specific flag version URI.
function deselect_version_uri(span_name, uri) {
	// Init.
	r = 0;
	// Update version div.
	$.get("scripts/actions.php?req=deselect_version_uri&uri=" + uri, function(r) {
		// Re-write span.
//			$('#' + span_name).attr('class', r).fadeIn('slow');
			// Change checkbox image source.
			$("#img_checkbox_" + span_name).attr("src", "images/checkbox" + r + ".png");
	});
}

// Get JSON payload for a specific flag-version URI and then update link in page.
function get_json_payload_for_uri(u, n, n_fmt) {
	// Change image to retrieving segments.
	$('#img_get_json_' + n_fmt).attr('src', 'images/retrieving_segments_mini.gif');
	// Update version div.
	$.get("scripts/actions.php?req=build_individual_json_payload&uri=" + u , function(r) {
		// If result retrieved
		if(r != 0) {
			// Set new contents.
			h = '<a href="' + r + '" target="_blank">' + n + '</a>';
			// Update span contents.
			$('#span_json_link_' + n_fmt).html(h);
			// Change image back again.
			$('#img_get_json_' + n_fmt).attr('src', 'images/arrow_on_blue.png');
		}
	});
}

// Retrieve segments.
function retrieve_segments() {
	// Get GPS start and stop times.
	s = $("#gps_start_time").val();
	e = $("#gps_stop_time").val();
	// Get file format ID.
	format = $('input[name=format]:checked', '#frm_query_server').val();
	// Hide button and show message.
	$("#divForsubmit_segment_form").fadeOut('fast');
	$("#img_retrieval_msg").fadeIn('fast');
	$("#img_retrieval_msg").css("visibility", "visible");
	// Update version div.
	$.get("scripts/actions.php?req=retrieve_segments&s=" + s + "&e=" + e + "&format=" + format, function(r) {
		// If result retrieved
		if(r != 0) {
			// Re-direct.
			window.open(r, '_self');
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
	$.get("scripts/actions.php?req=get_recent_query_results", function(r) {
		// If results retrieved.
		if(r != 0) {
			$('#div_payload_filter_form').html(r);
		}
	});
}

// Set the HWDB filter start page number.
function set_filter_start_page_no(p) {
	// Set mode.
	$.get("scripts/actions.php?req=set_filter_start_page_no&p=" + p, function() {
		// Re-build the Recent Query Results list.
		rebuild_recent_query_results_list();
	});
}

// De-/Activate the drop-down select for use in host changing.
function activate_host_change_option() {
	// Get current host box.
	$.get("scripts/actions.php?req=get_current_host_box", function(r) {
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
	$.get("scripts/actions.php?req=set_current_host&h=" + h, function() {
		// Reload page.
		location.reload();
	});
}

// Alternate the available flag_choice option.
function alternate_flag_option() {
	// Alternate flag choice option.
	$.get("scripts/actions.php?req=alternate_flag_choice_option", function(r) {
		// If result returned.
		if(r != 0) {
			$('#input_Flags_val').html(r);
		}
	});
}

// Upload list of filtered JSON payloads.
function update_payloads(c) {
	// Init.
	var user_id = $('#user_id').val();
	var data_id = $('#data_id').val();
	// Set session.
	$.get("scripts/actions.php?req=filter_json_payloads&c=" + c + "&u=" + user_id + "&d=" + data_id, function(r) {
		// If result returned.
		if(r != 0) {
			$('#div_payload_filter_form').html(r);
		}
	});
}

// Set file format PHP session.
function set_format(format_id) {
        // Set session.
        $.get("scripts/actions.php?req=set_format&f=" + format_id, function() {
        });
}