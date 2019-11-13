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
		$('#p-info').html(json[k]['text']);
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
	$("#div_ifo_" + ifo).removeClass('w3-blue');
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
/* Update the flag versions. */
function update_flag_versions(max) {
	// Get currently selected flag.
	var dq_flag = $("#dq_flag").val();
	// If number of elements in list is less than or equal to 10.
	if(dq_flag.length <= 10) {
		// Update version div.
		$.get("scripts/actions.php?action=update_version_div&dq_flag=" + dq_flag, function(r) {
			// If result retrieved
			if(r != 0) {
				// Show versions container.
				$('#div_versions').removeClass('w3-hide');
				// Re-write versions field.
				$('#div_versions_field').html(r);
				// Show retrieve segment button.
				$("#div_get_segments_button").removeClass("w3-hide");
			}
		});
	}
	// Otherwise, if number of elements in list is more than 10.
	else {
		open_warning_modal(get_too_many_flags_msg(dq_flag.length, max));
	}
}
/* Update the flag versions from a textarea. */
function update_div_flag_versions_from_ta($max) {
	// Set flag string.
	var f_string = "[\"" + $("#ta_dq_flag").val().replace(/\n/g, "\",\"") + "\"]";
	// Get currently selected IFO.
	var dq_flag_list = JSON.parse(f_string);
	// If number of elements in list is less than or equal to 10.
	if(dq_flag_list.length <= 10) {
		var dq_flag = $("#ta_dq_flag").val().replace(/\n/g, "[[[BREAK]]]");
		// Update version div.
		$.get("scripts/actions.php?action=update_version_div_from_ta&dq_flag=" + dq_flag, function(r) {
			// If result retrieved
			if(r != 0) {
				// Show versions container.
				$('#div_versions').removeClass('w3-hide');
				// Re-write versions field.
				$('#div_versions_field').html(r);
				// Show retrieve segment button.
				$("#div_get_segments_button").removeClass("w3-hide");
			}
		});
	}
	// Otherwise, if number of elements in list is more than 10.
	else {
		open_warning_modal(get_too_many_flags_msg(dq_flag_list.length, max));
	}
}
/* Get the too-many-flags-have-been-selected message. */
function get_too_many_flags_msg(len, max) {
	// Set.
	r = len + ' flags have currently been selected.\n\nThe maximum allowable limit via this interface is ' + max;
	// Return.
	return r;
}
/* Select/De-select a specific flag version URI. */
function select_version_uri(span_name, uri) {
	// Init.
	r = 0;
	// Update version div.
	$.get("scripts/actions.php?action=select_version_uri&uri=" + uri, function(r) {
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
	$.get("scripts/actions.php?action=get_segments&s=" + s + "&e=" + e + "&format=" + f + "&history=" + h, function(r) {
		// If result retrieved
		if(r != 0) {
			// Re-direct.
			window.open(r, '_self');
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


});
