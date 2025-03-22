function delta(end, start) {
	//end, start are unix timestamps
	diff = parseInt(end, 10) - parseInt(start, 10); //diff is in seconds
	msec = diff*1000;
	var hh = Math.floor(msec / 1000 / 60 / 60);
	msec -= hh * 1000 * 60 * 60;
	var mm = Math.floor(msec / 1000 / 60);
	msec -= mm * 1000 * 60;
	var ss = Math.floor(msec / 1000);
	msec -= ss * 1000;

	if(hh === 0) {
		if(mm === 0) {
			return ss + 's';
		}
		return mm + 'min ' + ss + 's';
	}
	return hh + 'h ' + mm + 'm ' + ss + 's';
}
$(function() {
		"use strict";
		RecAPI.get_archive().success(function(archive) {
			/* To get sorted traversal, we need to do an array containing keys */
			var keys = [];
			for(var prop in archive) {
				keys.push(prop);
			}
			keys.sort(function(a,b) { return b - a; }); //descending

			/* ok, now we can traverse the objects */
			for(var i =0; i < keys.length; i++) {
				var rec = archive[keys[i]];
				console.log(rec);
				var name = $('<td/>').text(rec.name);
				var start = $('<td/>').text(config.date_read(
						parseInt(rec.starttime, 10)).toLocaleString()
					);
				var duration = $('<td/>').text(delta(rec.endtime, rec.starttime));
				var dl_text = $('<span/>').text(" Scarica").addClass('pure-hidden-phone');
				var fn = $("<td/>")
				if(rec.ready) {
					fn.append($("<a/>").prop("href", "/output/" + rec.filename)
						.addClass("pure-button pure-button-small")
						.html( $("<i/>").addClass("fa fa-download").css("color", "green"))
						.append(dl_text));
				} else {
					fn.html("<small>File not found</small>")
				}
				var row = $('<tr/>').append(name).append(start).append(duration).append(fn);
				row.data('id', rec.id)
				$('#ongoing-recs-table tbody').append(row);
			}
			});
		});

