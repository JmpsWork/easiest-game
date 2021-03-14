# LEVEL.JSON

Keyvalue | Description | Type | Mandatory? | Default
------------ | ------------- | ------------- | ------------- | -------------
``blurb`` | Text which is displayed before this level plays | ``str`` | **Yes** | None
``tutorial_text`` | Text which is shown constantly at the top of the screen during a level | ``str`` | No | ''
``centered`` | Should this level be visually centered in the screen? | ``bool`` | No | ``false``
``next_level`` | The next level loaded once this one is completed. Can be false. | ``bool`` or ``str`` | No | ``false``
``spawnx`` | The player's initial X origin coordinate. | ``int`` | No | ``50``
``spawny`` | The player's initial Y origin coordinate. | ``int`` | No | ``50``
``tiles`` | A list of all tiles in the level. More info can be found below. | ``list`` | **Yes** | None
``walls`` | A list of all walls in the level. More info can be found below. | ``list`` | **Yes** | None
``enemies`` | A list of all enemies in the level. More info can be found below. | ``list`` | No | []
``coins`` | A list of all coins in the level. More info can be found below. | ``list`` | No | []
``keys`` | A list of all keys in the level. More info can be found below. | ``list`` | No | []


### TILES

Keyvalue | Description | Type | Mandatory? | Default
------------ | ------------- | ------------- | ------------- | -------------
``template`` | Tile inherits values from the tile with this name from ``tiletemplates.json`` | ``str`` | **Yes** | None
``color`` | The RGB value of this tile. | ``list`` | No | ``[180, 180, 220]``
``nil`` | Tile will never be drawn or interacted with. | ``bool`` | No | ``false``
``end_level`` | If the player can complete the level and is touching this tile, the level will end. | ``bool`` | No | ``false``
``checkpoint`` | If the player touches this tile, they can have their respawn point changed. | ``bool`` | No | ``false``
``newx`` | When the player touches this tile, this will be their new spawn point X coordinate if ``checkpoint`` is true. | ``int`` | No | ``0``
``newx`` | When the player touches this tile, this will be their new spawn point Y coordinate if ``checkpoint`` is true. | ``int`` | No | ``0``
``warp`` | If the player touches this tile, they will be teleported to this tile's warp coordinates. | ``bool`` | No | ``false``
``warpx`` | The X coordinate to be teleported to.| ``int`` | No | ``0``
``warpy`` | The Y coordinate to be teleported to. | ``int`` | No | ``0``


### WALLS

Keyvalue | Description | Type | Mandatory? | Default
------------ | ------------- | ------------- | ------------- | -------------
``sx`` | The Wall's starting X coordinate. | ``int`` | **Yes** | None
``sy`` | The Wall's starting Y coordinate. | ``int`` | **Yes** | None
``ex`` | The Wall's ending X coordinate. | ``int`` | **Yes** | None
``ey`` | The Wall's ending Y coordinate. | ``int`` | **Yes** | None
``color`` | The RGB value of this wall. | ``list`` | No | ``[0, 0, 0]``
``id`` | Any key collected with a matching ``id`` to this wall will have their collision disabled. | ``int`` | No | None


### ENEMIES

Keyvalue | Description | Type | Mandatory? | Default
------------ | ------------- | ------------- | ------------- | -------------
``x`` | This enemy's inital X coordinate. | ``int`` | **Yes** | None
``y`` | This enemy's inital Y coordinate. | ``int`` | **Yes** | None
``speed`` | This enemy's speed, if enemy uses ``path`` this will be the speed in pixels, if this enemy uses ``pivot`` this will be speed in degrees per second. | ``int`` | No | ``0`` 
``path`` | A list of coordinate pairs. The enemy will follow these points. Once it reaches the final point it will travel back to its first point. | ``list`` | No | []
``pivot`` | A coordinate pair. The enemy will 'orbit' around this point from their current position. Mutually exclusive with ``path`` | ``list`` | No | []
``color`` | This enemy's RGB color. | ``list`` | No | ``[50, 50, 230]``


### COINS

Keyvalue | Description | Type | Mandatory? | Default
------------ | ------------- | ------------- | ------------- | -------------
``x`` | This coin's inital X coordinate. | ``int`` | **Yes** | None
``y`` | This coin's inital Y coordinate. | ``int`` | **Yes** | None


### KEYS

Keyvalue | Description | Type | Mandatory? | Default
------------ | ------------- | ------------- | ------------- | -------------
``x`` | This key's inital X coordinate. | ``int`` | **Yes** | None
``y`` | This key's inital Y coordinate. | ``int`` | **Yes** | None
``color`` | This key's RGB color. | ``list`` | No | ``[255, 255, 255]``
``id`` | This key's ID. When a key is collected, any walls with the same ID as this key will be unlocked. | ``int`` | **Yes** | None


# CAMPAIGN.JSON

Keyvalue | Description | Type | Mandatory? | Default
------------ | ------------- | ------------- | ------------- | -------------
``name`` | The name of this campaign. | ``str`` | **Yes** | None
``difficulty`` | The difficulty of this campaign. ``-1`` = Tutorial, ``0`` = Easy, ``1`` = Medium, ``2`` = Hard, ``3`` = Expert, ``4`` = Special, ``99`` = Testing | ``str`` | **Yes** | None
``levels`` | A list of all levels in this campaign. These will show up in the level selection menu. | ``str`` | **Yes** | None
``required_score`` | Unused. | ``int`` | No | None
