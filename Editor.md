# LEVEL EDITOR

This game comes with a small but fairly effective level edtior for quickly creating 
level geometry and enemy paths without having to manually enter the necessary values in to a json file.

The level editor can be opened by running ``editor.py``.

Currently, the level editor does not support the accurate placement of anything, cannot place down coins,
cannot place down keys, and cannot edit the properties of placed down things.
It cannot open or edit existing levels either, so it's more of a tool to quickly place the bulk of geometry down.

### UI

The UI is very minimalistic, and shows a handful of things. It will show:
* The X and Y coordinate of the cursor relative to the origin.
* The same as above but converted to tile coordinates.
* The origin of the level is marked by 2 lines; the red line being the positive X axis and the blue line being the positive Y axis.
* The currently used ``mode`` is shown on the top right of the screen.
* If the mode is 1, the tile currently being used will be shown to the left of the ``mode``.

### CONTROLS

* W A S D | Respectively pan the editor camera up, right, down and left.
* Left Click | Depending on the mode, add or extend the placement of something.
* Right Click | Remove previously created element.
* Scroll Wheel | If the ``mode`` is set to 1, this will change the tile currently being used.
* ESC | Closes the editor.
* 1 | Sets the ``mode`` to 1.
* 2 | Sets the ``mode`` to 2.
* 3 | Sets the ``mode`` to 3.
* C | Centers the placement of objects in the middle of a tile instead of the corner. Defaults to off.
* R | Exports the level to ``editorlevel.json``. It will also automatically center the level to the origin (marked by the red and blue lines).
* O | Allows currently existing tiles to be overwritten with whatever tile is currently selected. Defaults to off.
* F | Toggles wall fixup. By default, it is toggled on. It is recommended to leave this on, as otherwise the player can easily get stuck in overlapping wall geometry.
* P | Set the spawnpoint of the player to this tile. Affected by the centered option.
* KEYPAD_DELETE | Erase the current level.
* KEYPAD_0 | Simulates the movement of enemies. Jank, Cannot be turned off.
* KEYPAD_ENTER | If the ``mode`` is 3, this will place an enemy down using the current path.

### MODES

The level editor functions on the basis of 3 different modes, which allow the creation of different level elements.

1. MODE 1 | This mode is for the placement and removal of tiles. The only tiles which can be used are the ones in ``tiletemplates.json``.
2. MODE 2 | This mode is for the placement of walls. **Walls cannot be placed diagonally; otherwise they will create a much larger wall!**
3. MODE 3 | This mode is for the placement of enemy path points. A series of blue lines will show the path of the enemy created.
