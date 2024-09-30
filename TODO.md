## PRIORITY

Saves:
- Sometimes, the chunks and players directories are created in saves/, not in saves/save_name/
- Allow renaming saves

UI:
- Add key number on top of main bar
- Rename window

Render:
- Use surfaces to render chunks
- Rotate some blocks to be less repetitive (need surfaces)

Bugs:
- Seems like more of the time, the same world is generated
- Can place a block on the upper part of the player (head)

Others:
- Maybe go to C or C++ with SDL2
- Put games in separated processes
- Put different parts of games in separate threads to allow them running concurrently

## GENERATION:

- [ ] vertical chunks
- [x] biomes
- [x] water
- [x] ore veins
- [x] trees and forests
- [x] caves

- Remove floating blocks
  - (Generate caves only under surface?)
  
- Create caves before placing biome blocks


## SAVES AND LOADS:

- must be fast and memory efficient

- save and load: chunks, players' infos (place, inventory, ...)

## DISPLAY:

- [x] inventory
- [ ] life
- [ ] light
- [ ] command panel?

- responsive

## MOVES:

- [ ] with hitboxes and not only block by block
- [ ] left, right, down, up (ladders?)
- [x] fall

## UI/UX:

- [ ] allow changing keys
- [ ] orientation of the player with the mouse?
- [ ] interaction range

## INTERACTIONS WITH BLOCKS:

- [x] workbench (display required components, need quantity and actual quantity)
- [ ] furnace
- [ ] chest

## COMMANDS:

- [ ] teleportation
- [ ] give items
- [ ] display hitboxes

## MENUS:

- [x] main menu
- [x] params menu
- [x] load world menu
- [x] create world menu
- [ ] online menu

## MULTIPLAYER:

- [x] test multiplayer offline
- [x] send data
- [x] receive data
- [x] synchronize chunks loaded by multiple players
- [x] two separated programs for client and server (display, input) and (game management)
- [x] server can be runned at same time as playing (but separated)

## SONGS: