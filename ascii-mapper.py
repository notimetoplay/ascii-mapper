#!/usr/bin/env python3
# coding=utf-8
#
# ASCII Mapper: tile map editor for games using only ASCII characters.
# Copyright 2017-2019 Felix Pleșoianu <https://felix.plesoianu.ro/>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import division
from __future__ import print_function

import os.path
import json
import sys

if sys.version_info.major >= 3:
	from tkinter import *
	from tkinter import ttk
	from tkinter.messagebox import showinfo, showerror, askyesno
	from tkinter.filedialog import askopenfilename, asksaveasfilename
	from tkinter.colorchooser import askcolor
else:
	from Tkinter import *
	import ttk
	from tkMessageBox import showinfo, showerror, askyesno
	from tkFileDialog import askopenfilename, asksaveasfilename
	from tkColorChooser import askcolor

about_text = """
Creator: No Time To Play
Version: 2019-08-17
License: MIT
"""

map_width = 25
map_height = 25
map_filename = None
modified = False

map_tiles = [[None for i in range(map_width)] for i in range(map_height)]

def map_data(canvas, tiles):
	return ["".join(canvas.itemcget(i, "text") for i in j) for j in tiles]

def set_map_data(canvas, data):
	for y in range(len(map_tiles)):
		if y < len(data):
			for x in range(len(map_tiles[y])):
				t = map_tiles[y][x]
				if x < len(data[y]):
					char = data[y][x]
				else:
					char = filler
				canvas.itemconfigure(t, text=char)
		else:
			for t in map_tiles[y]:
				canvas.itemconfigure(t, text=filler)

zoom = 3
scale = zoom * 8
offset = scale

map_font = "courier " + str(scale * 3 // 4) + " bold"

brush = "#"
filler = "."
dragging = False

top = Tk()
top.title("ASCII Mapper")

grid_shown = BooleanVar() # Can only be used after calling Tk().

def redraw_grid(canvas):
	color = canvas.itemcget("grid", "fill")
	canvas.delete("grid")
	y1 = offset
	y2 = offset + map_width * scale
	for x in range(map_width + 1):
		x1 = offset + x * scale
		x2 = x1
		canvas.create_line(
			x1, y1, x2, y2,
			dash=".", tags="grid")
	x1 = offset
	x2 = offset + map_height * scale
	for y in range(map_height + 1):
		y1 = offset + y * scale
		y2 = y1
		canvas.create_line(
			x1, y1, x2, y2,
			dash=".", tags="grid")
	if color != "":
		canvas.itemconfigure("grid", fill=color)

def set_grid_by_state(canvas):
	if not grid_shown.get():
		canvas.itemconfigure("grid", state="hidden")
	else:
		canvas.itemconfigure("grid", state="normal")

def toggle_tile(t):
	def do_toggle(event):
		global modified
		if event.widget.itemcget(t, "text") != brush:
			event.widget.itemconfigure(t, text=brush)
		else:
			event.widget.itemconfigure(t, text=filler)
		modified = True
	return do_toggle

def redraw_map(canvas):
	canvas.delete("tile")
	for y in range(map_height):
		for x in range(map_width):
			tx = offset + x * scale + scale // 2
			ty = offset + y * scale
			t = canvas.create_text(tx, ty, text=filler,
				font=map_font, anchor="n", tags="tile")
			canvas.tag_bind(t, "<1>", toggle_tile(t))
			map_tiles[y][x] = t

def set_zoom(canvas, z):
	global zoom, scale, offset, map_font
	
	zoom = max(int(z), 1)
	scale = zoom * 8
	offset = scale

	w = map_width * scale + offset * 2
	h = map_height * scale + offset * 2
	canvas["scrollregion"] = (0, 0, w, h)

	map_font = "courier " + str(scale * 3 // 4) + " bold"
	canvas.itemconfigure("tile", font=map_font)
	
	for y in range(map_height):
		for x in range(map_width):
			tx = offset + x * scale + scale // 2
			ty = offset + y * scale
			t = map_tiles[y][x]
			canvas.coords(t, tx, ty)
	
	redraw_grid(canvas)
	set_grid_by_state(canvas)
	
	status["text"] = "Zoom level set to " + str(zoom) + "."

work_area = ttk.Frame(top)
work_area.columnconfigure(0, weight=1)
work_area.rowconfigure(0, weight=1)

viewport = Canvas(work_area, scrollregion="0 0 650 650")
viewport.grid(row=0, column=0, sticky="nsew")

v_scroll = ttk.Scrollbar(
	work_area,
	orient=VERTICAL,
	command=viewport.yview)
viewport["yscrollcommand"] = v_scroll.set
v_scroll.grid(row=0, column=1, sticky="ns")

h_scroll = ttk.Scrollbar(
	work_area,
	orient=HORIZONTAL,
	command=viewport.xview)
viewport["xscrollcommand"] = h_scroll.set
h_scroll.grid(row=1, column=0, sticky="ew")

def start_dragging():
	global dragging
	dragging = True

def paint_tiles(event):
	global modified
	if dragging:
		x = event.widget.canvasx(event.x)
		y = event.widget.canvasy(event.y)
		t = event.widget.find("closest", x, y)
		event.widget.itemconfigure(t, text=brush)
		modified = True

def stop_dragging():
	global dragging
	dragging = False

viewport.bind("<ButtonPress-1>", lambda e: start_dragging())
viewport.bind("<Motion>", paint_tiles)
viewport.bind("<ButtonRelease-1>", lambda e: stop_dragging())

user_width = IntVar()
user_width.set(25)
user_height = IntVar()
user_height.set(25)

props_dlg = Toplevel(top)
props_dlg.transient(top)
props_dlg.title("Map properties")
props_dlg.protocol("WM_DELETE_WINDOW", props_dlg.withdraw)
props_dlg.bind("<Key-Escape>", lambda e: props_dlg.withdraw())
props_dlg.resizable(FALSE, FALSE)
props_dlg.withdraw()

def resize_map():
	global map_width, map_height, map_tiles, modified
	
	data = map_data(viewport, map_tiles)
	map_width = user_width.get()
	map_height = user_height.get()
	map_tiles = [[None for i in range(map_width)]
		for i in range(map_height)]
	redraw_map(viewport)
	set_map_data(viewport, data)
	modified = True
	redraw_grid(viewport)
	set_grid_by_state(viewport)
	w = map_width * scale + offset * 2
	h = map_height * scale + offset * 2
	viewport["scrollregion"] = (0, 0, w, h)
	props_dlg.withdraw()

def cancel_resize():
	user_width.set(map_width)
	user_height.set(map_height)
	props_dlg.withdraw()

filename_label = ttk.Label(props_dlg, text="Filename: (untitled)")
filename_label.grid(row=0, column=0, columnspan=2, padx=4, pady=4)

filler_label = ttk.Label(props_dlg, text="Filler char: " + filler)
filler_label.grid(row=1, column=0, columnspan=2, padx=4, pady=4)

def set_filler_from_brush():
	global filler
	filler = brush
	filler_label["text"] = "Filler char: " + filler

ttk.Button(
	props_dlg,
	text="Set from brush",
	command=set_filler_from_brush,
	underline=9).grid(row=2, column=0, columnspan=2, padx=4, pady=4)

ttk.Label(props_dlg,
	text="Map width",
	underline=4).grid(
		row=3, column=0,
		padx=4, pady=4,
		sticky="w")
Spinbox(
	props_dlg,
	from_=5, to=100, increment=1,
	width=3,
	textvariable=user_width).grid(row=3, column=1, padx=4, pady=4)
ttk.Label(props_dlg,
	text="Map height",
	underline=4).grid(
		row=4, column=0,
		padx=4, pady=4,
		sticky="w")
Spinbox(props_dlg,
	from_=5, to=100, increment=1,
	width=3,
	textvariable=user_height).grid(row=4, column=1, padx=4, pady=4)

props_bar = ttk.Frame(props_dlg)
ttk.Button(
	props_bar,
	text="Cancel",
	width=6,
	command=cancel_resize,
	underline=0).pack(side=RIGHT, padx=4, pady=4)
ttk.Button(
	props_bar,
	text="Resize",
	width=6,
	command=resize_map,
	underline=0).pack(side=RIGHT, padx=4, pady=4)
props_bar.grid(row=5, column=0, columnspan=2)

def load_file(full_path):
	global modified
	
	fn = os.path.basename(full_path)
	name, ext = os.path.splitext(fn)
	try:
		with open(full_path) as f:
			if ext == ".json":
				data = json.load(f)
			else:
				data = [line for line in f]
		set_map_data(viewport, data)
		modified = False
		status["text"] = "Opened " + fn
		filename_label["text"] = "Map name: " + name
		top.title(fn + " | ASCII Mapper")
		return True
	except OSError as e:
		showerror("Error opening file", str(e), parent=top)
		return False
	except IOError as e: # For Python 2.7
		showerror("Error opening file", str(e), parent=top)
		return False

def save_file(full_path):
	global modified
	
	fn = os.path.basename(full_path)
	name, ext = os.path.splitext(fn)
	data = map_data(viewport, map_tiles)
	try:
		with open(full_path, "w") as f:
			if ext == ".json":
				json.dump(data, f)
			else:
				f.write("\n".join(data))
				f.write("\n")
			f.flush()
		modified = False
		status["text"] = "Saved " + fn
		filename_label["text"] = "Map name: " + name
		top.title(fn + " | ASCII Mapper")
		return True
	except OSError as e:
		showerror("Error opening file", str(e), parent=top)
		return False
	except IOError as e: # For Python 2.7
		showerror("Error opening file", str(e), parent=top)
		return False

def new_command():
	global map_filename, modified
	
	if modified:
		do_new = askyesno(
			title="New map?",
			message="Map is unsaved. Begin anew?",
			icon="question",
			parent=top)
		if not do_new:
			status["text"] = "New map canceled."
			return
	for y in range(map_height):
		for x in range(map_width):
			viewport.itemconfigure(map_tiles[y][x], text=filler)
	map_filename = None
	modified = False

def open_command():
	global map_filename
	
	if modified:
		do_open = askyesno(
			title="Open another map?",
			message="Map is unsaved. Open another?",
			icon="question",
			parent=top)
		if not do_open:
			status["text"] = "File opening canceled."
			return
	choice = askopenfilename(
		title="Open existing map",
		filetypes=('"ASCII maps" {.json .txt}', ("All files", ".*")),
		parent=top)
	if choice == "":
		status["text"] = "File opening canceled."
	elif not os.path.isfile(choice):
		showerror(
			"Error opening file",
			"File not found: " + choice,
			parent=top)
	elif load_file(choice):
		map_filename = choice

def save_command():
	if map_filename == None:
		saveas_command()
	else:
		save_file(map_filename)

def saveas_command():
	global map_filename
	
	choice = asksaveasfilename(
		title="Save map as...",
		filetypes=(("ASCII maps", ".json"), ("Plain text", ".txt")),
		parent=top)
	if len(choice) <= 0:
		status["text"] = "Save canceled."
	elif save_file(choice):
		map_filename = choice

def reload_command():
	if map_filename == None:
		showinfo("Oops!", "The map was never saved.", parent=top)
	else:
		do_open = askyesno(
			title="Reload map?",
			message="Reload map from last save?",
			icon="question",
			parent=top)
		if not do_open:
			status["text"] = "File reloading canceled."
			return
		else:
			load_file(map_filename)

def show_about():
	showinfo("About ASCII Mapper", about_text, parent=top)

def confirm_quit():
	if modified:
		do_quit = askyesno(
			title="Quit ASCII Mapper?",
			message="Map is unsaved. Quit anyway?",
			icon="question",
			parent=top)
	else:
		do_quit = True
	if do_quit:
		top.destroy()
	else:
		status["text"] = "Quit canceled."

toolbar = ttk.Frame(top)
toolbar.pack(side=TOP, fill="x", padx=4, pady=4)

brush_view = ttk.Label(
	toolbar, width=2, font=map_font, text=brush, anchor="center")
brush_view.pack(side=LEFT)

ttk.Separator(toolbar, orient=VERTICAL).pack(side=LEFT, padx=4)

def toolbutt(txt, under=None, cmd=None):
	return ttk.Button(
		toolbar,
		text=txt,
		underline=under,
		#image=img,
		#compound="left",
		command=cmd)

toolbutt("New", 0, new_command).pack(side=LEFT)
toolbutt("Open", 0, open_command).pack(side=LEFT)
toolbutt("Save", 0, save_command).pack(side=LEFT)

ttk.Separator(toolbar, orient=VERTICAL).pack(side=LEFT, padx=4)

toolbutt("Save as", 5, saveas_command).pack(side=LEFT)
toolbutt("Reload", 0, reload_command).pack(side=LEFT)

ttk.Separator(toolbar, orient=VERTICAL).pack(side=LEFT, padx=4)

toolbutt("Properties", 0, props_dlg.deiconify).pack(side=LEFT)
toolbutt("About", 1, show_about).pack(side=LEFT)

def pick_background():
	color = askcolor(initialcolor=viewport["background"])
	if color[1] != None:
		viewport["background"] = color[1]
		brush_view["background"] = color[1]

def pick_foreground():
	color = askcolor(initialcolor=viewport.itemcget("tile", "fill"))
	if color[1] != None:
		viewport.itemconfigure("tile", fill=color[1])
		brush_view["foreground"] = color[1]

def pick_grid_color():
	color = askcolor(initialcolor=viewport.itemcget("grid", "fill"))
	if color[1] != None:
		viewport.itemconfigure("grid", fill=color[1])

view_menu = Menu(top, tearoff=0)
view_menu.add_command(
	label="Zoom in", underline=5, accelerator="Ctrl-+",
	command=lambda: set_zoom(viewport, zoom + 1))
view_menu.add_command(
	label="Zoom out", underline=5, accelerator="Ctrl--",
	command=lambda: set_zoom(viewport, zoom - 1))
view_menu.add_separator()
view_menu.add_checkbutton(
	label="Show grid",
	underline=5,
	accelerator="Ctrl-G",
	variable=grid_shown,
	onvalue=True,
	offvalue=False,
	command=lambda: set_grid_by_state(viewport))
view_menu.add_separator()
view_menu.add_command(
	label="Background...", underline=0, command=pick_background)
view_menu.add_command(
	label="Foreground...", underline=0, command=pick_foreground)
view_menu.add_command(
	label="Grid color...", underline=5, command=pick_grid_color)

statusbar = ttk.Frame(top)
statusbar.pack(side=BOTTOM, fill="x", padx=4, pady=4)
status = ttk.Label(statusbar, relief="sunken",
	text="Press any key to set the brush.")
status.pack(side=LEFT, ipadx=4, ipady=4, fill="x", expand=1)
ttk.Menubutton(
	statusbar,
	text="View",
	underline=2,
	menu=view_menu,
	direction="above").pack(side=RIGHT)
ttk.Separator(statusbar, orient=VERTICAL).pack(side=RIGHT, padx=4)

palette = ttk.Frame(top)
palette.pack(side=LEFT, fill="y", padx=4, pady=4)

def brush_setter(char):
	def do_set():
		global brush
		brush = char
		brush_view["text"] = brush
	return do_set

for i in """.,:;#=/+"~|^&*<>()[]?!$%""":
	ttk.Button(palette, text=i, width=2,
		command=brush_setter(i)).pack(side=TOP)

work_area.pack(side=RIGHT, fill="both", expand=1, padx=4, pady=4)

def set_brush_by_key(event):
	global brush
	if len(event.char) > 0:
		brush = event.char
		brush_view["text"] = brush

top.bind("<KeyPress>", set_brush_by_key)

def toggle_grid(canvas, flag):
	flag.set(not flag.get())
	set_grid_by_state(canvas)

top.bind("<Control-n>", lambda e: new_command())
top.bind("<Control-o>", lambda e: open_command())
top.bind("<Control-s>", lambda e: save_command())
top.bind("<Control-r>", lambda e: reload_command())
top.bind("<Control-q>", lambda e: confirm_quit())

top.protocol("WM_DELETE_WINDOW", confirm_quit)

top.bind("<Control-equal>", lambda e: set_zoom(viewport, zoom + 1))
top.bind("<Control-minus>", lambda e: set_zoom(viewport, zoom - 1))
top.bind("<Control-g>", lambda e: toggle_grid(viewport, grid_shown))

redraw_grid(viewport)
redraw_map(viewport)
set_grid_by_state(viewport)

top.mainloop()
