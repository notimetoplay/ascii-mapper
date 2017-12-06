ASCII Mapper
============


Ever needed a map editor for a tile-based game, but found most of them too complicated and/or specific? ASCII Mapper allows you to paint the same using the characters on your keyboard instead of graphics. That's it: just a grid of symbols you can load easily in code and interpret however you want.

Other ASCII art editors exist. This one differs from them in two big ways:

1. It uses square tiles, so you can estimate distances well.
2. It doesn't deal in color, to keep it abstract and distraction-free.

But how will I know what all the symbols mean?
----------------------------------------------

Why, they mean whatever you want them to. It's your game, and your maps.

That said, games in the roguelike genre have established certain conventions you might want to follow, to avoid having to make up your own:

	. is the default, empty floor
	, is a marked floor that stands out in some way
	: is impassable terrain
	; is another type of impassable terrain
	# is a wall
	~ is water
	| is a column, pole or tree trunk
	^ is a mountain or pine tree
	" is a bush or foliage of some sort
	+ is a closed door
	/ is an open door
	= is a wooden plank, table or crate
	< is a staircase going up
	> is a staircase going down

You can also use any other character on the keyboard; just press any key you want to set the brush. For instance, I've used "*" to mean a fountain or basin, and "&" to mean a statue.

Limitations
-----------

ASCII Mapper handles maps of up to 100x100. You can't fit much more in a reasonably-sized browser window anyway, even at minimum zoom. A future version might put the map in a scrollable viewport of its own.

