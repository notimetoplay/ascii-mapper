$(document).ready(function() {
	"use strict";
	
	var map_width = 25;
	var map_height = 25;
	var map_data = make_map(map_width, map_height);
	
	var mx = -1;
	var my = -1;
	var dragging = false;
	var brush = "#";
	var last_brush = brush;
	var zoom_level = 3;
	var zoom_step = 8;
	var zoom = zoom_level * zoom_step;
	
	var display = $("#map-display").get(0);
	var ctx = display.getContext("2d");

	ctx.font = zoom + "px Square";
	ctx.textAlign = "left";
	ctx.textBaseline = "top";
	
	function make_map(width, height) {
		var data = new Array(map_height);
	
		for (var y = 0; y < height; y++) {
			data[y] = new Array(width);
			for (var x = 0; x < width; x++) {
				data[y][x] = '.';
			}
		}
		
		return data;
	}
	
	function copy_all(source, dest) {
		var height = Math.min(source.length, dest.length);
		for (var y = 0; y < height; y++) {
			var width = Math.min(source[y].length, dest[y].length);
			for (var x = 0; x < width; x++) {
				dest[y][x] = source[y][x];
			}
		}
	}
	
	function set_tile(x, y) {
		map_data[y][x] = brush;
	}
	
	function redraw_tile(x, y) {
		ctx.fillStyle = "black";
		ctx.fillRect(x * zoom, y * zoom, zoom, zoom);
		ctx.fillStyle = "white";
		ctx.fillText(map_data[y][x], x * zoom, y * zoom);
	}
	
	function refresh() {
		display.width = map_width * zoom;
		display.height = map_height * zoom;

		ctx.font = zoom + "px Square";
		ctx.textAlign = "left";
		ctx.textBaseline = "top";
		
		ctx.fillStyle = "black";
		ctx.fillRect(0, 0, display.width, display.height);
		
		ctx.fillStyle = "white";
		for (var y = 0; y < map_height; y++) {
			for (var x = 0; x < map_width; x++) {
				ctx.fillText(
					map_data[y][x], x * zoom, y * zoom);
			}
		}
	}
	
	refresh();
	$("#map-source").val("");
	$("#zoom").val(zoom_level);
	$("#map-width").val(map_width);
	$("#map-height").val(map_height);
	
	$(display).mousedown(function(event) {
		mx = event.clientX - $(this).offset().left;
		my = event.clientY - $(this).offset().top;
		mx = Math.floor(mx / zoom);
		my = Math.floor(my / zoom);
		$("#coords").text(mx + ", " + my);
		set_tile(mx, my);
		redraw_tile(mx, my);
		//refresh();
		dragging = true;
	});
	
	$(display).mousemove(function(event) {
		var x = event.clientX - $(this).offset().left;
		var y = event.clientY - $(this).offset().top;
		x = Math.floor(x / zoom);
		y = Math.floor(y / zoom);
		$("#coords").text(x + ", " + y);

		if (!dragging) return;
		
		if (x !== mx || y !== my) {
			set_tile(x, y);
			redraw_tile(x, y);
			//refresh();
			mx = x;
			my = y;
		}
	});
	
	$(display).mouseup(function(event) {
		dragging = false;
		$("#coords").text("");
	});
	
	$(display).mouseout(function(event) {
		dragging = false;
		$("#coords").text("");
	});
	
	$(window).keypress(function(event) {
		if (event.altKey || event.ctrlKey || event.metaKey)
			return;
		
		var char = event.key || event.char;
		if (char.length === 1) {
			brush = char;
			if (brush != ".")
				last_brush = brush;
			$("#brush").val(char);
		}
	});
	
	$("#brush").click(function () {
		if (brush === ".") {
			brush = last_brush;
		} else {
			last_brush = brush;
			brush = ".";
		}
		$("#brush").val(brush);
	});
	
	$("#from-json").click(function () {
		var text = $("#map-source").val();
		
		if (text === "") {
			$("#map-source").val("Please enter data");
			return;
		}
		
		var new_data = null;
		
		try {
			new_data = JSON.parse(text);
		} catch (e) {
			console.log(e);
			return;
		}
		
		copy_all(new_data, map_data);
		refresh();
	});
	
	$("#from-text").click(function () {
		var text = $("#map-source").val();
		
		if (text === "") {
			$("#map-source").val("Please enter data");
			return;
		}
		
		var new_data = null;
		
		try {
			new_data = text.split("\n");
		} catch (e) {
			console.log(e);
			return;
		}
		
		copy_all(new_data, map_data);
		refresh();
	});
	
	$("#to-json").click(function () {
		var lines = new Array(map_height);
		for (var y = 0; y < map_height; y++) {
			lines[y] = map_data[y].join("");
		}
		$("#map-source").val(JSON.stringify(lines));
	});
	
	$("#to-text").click(function () {
		var lines = new Array(map_height);
		for (var y = 0; y < map_height; y++) {
			lines[y] = map_data[y].join("");
		}
		$("#map-source").val(lines.join("\n"));
	});
	
	var tools = [".", ",", ":", ";", "#", "~", "|", "=", "-", "+",
		"/", "\\", "^", "&", "*", '"', "`", "'", "<", ">"];
		
	for (var i = 0; i < tools.length; i++) {
		var palbtn = document.createElement("input");
		palbtn.type = "button";
		palbtn.value = tools[i];
		$("#palette").append(palbtn);
		if (i % 2 === 1)
			$("#palette").append(document.createElement("br"));
	}
	
	$("#palette input").click(function () {
		brush = this.value;
		if (brush != ".")
			last_brush = brush;
		$("#brush").val(this.value);
	});
	
	$("#zoom").change(function () {
		zoom_level = parseInt(this.value);
		zoom = zoom_level * zoom_step;
		refresh();
	});
	
	$("#new-map").click(function () {
		if (!confirm("Delete this map and start anew?"))
			return;
		
		map_width = parseInt($("#map-width").val());
		map_height = parseInt($("#map-height").val());
		map_data = make_map(map_width, map_height);
		refresh();
	});
	
	$("#resize-map").click(function () {
		if (!confirm("Some data may be lost Resize map?"))
			return;
		
		map_width = parseInt($("#map-width").val());
		map_height = parseInt($("#map-height").val());
		var new_data = make_map(map_width, map_height);
		copy_all(map_data, new_data);
		map_data = new_data;
		refresh();
	});
});
