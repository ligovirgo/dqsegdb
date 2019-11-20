/*
This file is part of the DQSEGDB WUI.

This file was written by Gary Hemming <gary.hemming@ego-gw.it>.

DQSEGDB WUI uses the following open source software:
- jQuery JavaScript Library v1.12.4, available under the MIT licence - http://jquery.org/license - Copyright jQuery Foundation and other contributors.
- W3.CSS by Jan Egil and Borge Refsnes.
- Font Awesome by Dave Gandy - http://fontawesome.io.
- Jquery Timepicker, developed and maintained by Willington Vega. Code licensed under the MIT and GPL licenses - http://timepicker.co
*/

/************************************
* AUTHENTICATION-RELATED FUNCTIONS *
**********************************/

/* Log a user out. */
/* Open the sign-in modal. */

/* Reload the page. */
function reload_page() {
    // Re-load the page.
	location.reload();
}

/* Go to a specific uri. */
function go_to_uri(uri) {
    // Go to.
	window.location.replace(uri);
}

/*******************************
* STRUCTURE-RELATED FUNCTIONS *
*****************************/

/* Open warning modal. */
function open_warning_modal(s) {
	// Add warning string.
	$("#p-warning").html(s);
	// Display.
	$("#warning-modal").css("display","block");
}
/* Close warning modal. */
function close_warning_modal() {
	$("#warning-modal").css("display","none");
}

/*********************
* GENERAL FUNCTIONS *
*******************/

/* Submit a form on return keypress. */
function entsub(event, area) {
	// If return.
	if(event && event.keyCode == 13) {
		// If authenticating.
		if(area == 'aut') {
			// Sign-in.
			submit_sign_in_form();
		}
	}
}

/* Clear an input value. */
function clear_value(inp) {
	// If the value being passed is the default value.
	if(inp.value == inp.defaultValue) {
		// Clear.
		inp.value = '';
	}
}

// Add leading zeroes to a number.
function pad_digits(number, digits) {
    return Array(Math.max(digits - String(number).length + 1, 0)).join(0) + number;
}

/* Get the on-screen position of an element. */
function get_element_position(e) {
    var offset = $(e).offset();
    var xPos = offset.left;
    var yPos = offset.top;
    alert('x: ' + xPos + '; y: ' + yPos);
}

/******************
* MODAL FUNCTIONS * 
******************/

/* Open the info modal. */
function open_info_modal(k) {
	// Get the JSON.
	$.getJSON("resources/info.json", function(json){
		// Set.
		$('#hdr-info').html(json[k]['title']);
		$('#div-info-contents').html(json[k]['text']);
		// Display.
		$("#info-modal").css("display","block");
	});
}
/* Close info modal. */
function close_info_modal() {
	$("#info-modal").css("display","none");
}
/********************
* SIDENAV FUNCTIONS * 
*********************/

/* Close all side-navigation bars. */
function close_sidenavs() {
	close_info_modal();
}

/******************************
* GET-SEGMENTS-FORM FUNCTIONS * 
******************************/

/* Build the Get Segments form. */
function build_get_segments_form() {
	$("#div_get_segments").html("<i class=\"fas fa-spinner w3-spin\"></i> Building Get-Segments form...");
	/* Check the connection to the server and output the Get-Segments form if available. */
	$.get("scripts/actions.php?action=build_get_segments_form", function(form) {
		$("#div_get_segments").addClass('w3-border');
		$("#div_get_segments").html(form);
	});

}
/* Set the output-format session value. */
function set_output_format(f) {
	$.get("scripts/actions.php?action=set_output_format&f=" + f, function() {
	});
}
/* Set the include-history session value. */
function set_include_history(ih) {
	$.get("scripts/actions.php?action=set_include_history&ih=" + ih, function() {
	});
}
/* Set the choose-flag-option value. */
function switch_choose_flag_option() {
	$("#div_choose_flag_option").html("<p><i class=\"fas fa-spinner w3-spin\"></i> Rebuilding choose-flag options...</p>");
	$.get("scripts/actions.php?action=switch_choose_flag_option", function(r) {
		$("#div_choose_flag_option").html(r);
	});
}
/* Select/Deselect an IFO. */
function deselect_ifo(ifo) {
	$.get("scripts/actions.php?action=deselect_ifo&ifo=" + ifo, function(r) {
		// If IFO is deselected.
		if(r == 1) {
			$("#div_ifo_" + ifo).removeClass('w3-blue');
			$("#div_ifo_" + ifo).addClass('w3-white');
		}
		else {
			$("#div_ifo_" + ifo).addClass('w3-blue');
			$("#div_ifo_" + ifo).removeClass('w3-white');
		}
		update_flags_multiple_ifo();
	});
}
/* Update the flags. */
function update_flags_multiple_ifo() {
	$('#div_choose_flag_option').html("<i class=\"fas fa-spinner w3-spin\"></i> Re-building flag list...");
	// Update.
	$.get("scripts/actions.php?action=update_flags_multiple_ifo", function(r) {
		// Re-write form.
		$('#div_choose_flag_option').html(r);
	});
}
/* Update the flags. */
function update_flags() {
	// Get currently selected IFO.
	var ifo = $("#ifo").val();
	// Update.
	$.get("scripts/actions.php?action=update_flags&ifo=" +  ifo, function(r) {
		// Re-write form.
		$('#div_choose_flag_option').html(r);
	});
}
/* Filter the flag list */
function filter_flag_list() {
	var ff = $("#flag_filter").val();
	$.get("scripts/actions.php?action=update_flag_filter&ff=" + ff, function(r) {
		update_flags_multiple_ifo();
	});
}
/* Select a flag. */
function select_flag(ifo_flag) {
	$.get("scripts/actions.php?action=check_number_of_selected_flags", function(check) {
		// If number of selected flags is OK.
		if(check == 0) {
			$.get("scripts/actions.php?action=select_flag&dq_flag=" + ifo_flag, function(r) {
				// Remove from the flag list.
				$("#li_" + ifo_flag).addClass('w3-hide');
				// Update the flag verions.
				update_flag_versions();
			});
		}
		// Otherwise, if too many flags have been selected.
		else {
			$.get("scripts/actions.php?action=get_max_selected_flags", function(max) {
				m = 'It is possible to select ' + max + ' flags. This limit has been reached. To select more flags, it will first be necessary to deselect others.';
				// Set.
				open_warning_modal(m);
			});
		}
	});
}
/* Deselect a flag from the versions container. */
function deselect_flag(ifo_flag, max) {
	$.get("scripts/actions.php?action=deselect_flag&dq_flag=" + ifo_flag, function(r) {
		// Add back in to the flag list.
		$("#li_" + ifo_flag).removeClass('w3-hide');
		// Update the flag verions.
		update_flag_versions();
	});
}
/* Update the flag versions. */
function update_flag_versions() {
	// Update version div.
	$.get("scripts/actions.php?action=update_version_div", function(r) {
		// Show versions container.
		$('#div_versions').removeClass('w3-hide');
		// Re-write versions field.
		$('#div_versions_field').html(r);
		// Show retrieve segment button.
		$("#div_get_segments_button").removeClass("w3-hide");
	});
}
/* Select/De-select a specific flag version URI. */
function select_version(ifo_flag, v) {
	// Update version div.
	$.get("scripts/actions.php?action=select_version&ifo_flag=" + ifo_flag + '&v=' + v, function(r) {
	});
}
/* Get segments. */
function get_segments() {
	$("#btn_get_segments").addClass("w3-hide");
	$("#p_getting_segments").removeClass("w3-hide");
	// Get GPS start and stop times.
	s = $("#gps_start_time").val();
	e = $("#gps_stop_time").val();
	// Get file format ID.
	f = $('input[name=output_format]:checked').val();
    h = $('input[name=include_history]:checked').val();
	// Update version div.
	$.get("scripts/actions.php?action=get_segments&s=" + s + "&e=" + e + "&format=" + f + "&history=" + h, function(f) {
		// If result retrieved
		if(f != 0) {
			// Re-direct.
            //window.open(r, '_self');
            go_to_uri('?c=2&f=' + f);
		}
		// Show button and hide message.
		$("#span_getting_segments").addClass("w3-hide");
		$("#btn_get_segments").removeClass("w3-hide");
	});
}

/****************************
* DOCUMENT-READY FUNCTIONS * 
**************************/

$(document).ready(function(){

	/* Set the Search-from date-picker. */
	$('.datepicker_onload').datepicker({
		  dateFormat: "dd-mm-yy"
	});

	$('.timepicker').timepicker({
	    timeFormat: 'HH:mm',
	    interval: 15,
	    dynamic: false,
	    dropdown: true,
	    scrollbar: true
	});
	
	/* Check the connection to the server and output the Get-Segments form if available. */
	$.get("scripts/actions.php?action=check_host_connection", function(status) {
		// If connection established.
		if(status == 1) {
			$("#p_get_segments").html("<i class=\"fas fa-check-circle\"></i> Connection to host established");
			build_get_segments_form();
		}
		// Otherwise, if unable to establish connection.
		else {
			$("#p_get_segments").html("<i class=\"fas fa-exclamation-circle\"></i> Connection unavailable. Explanation + Instructions...");
			$("#p_get_segments").addClass("w3-text-red");
		}
	});

	/* When the view-segments is ready, load in the latest results. */
	$('#div_view_segments').ready({
		$.get("scripts/actions.php?action=get_latest_query_results", function(r) {
			$('#div_view_segments').html(r);
		}
	});

});
