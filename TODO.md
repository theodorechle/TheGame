## PRIORITY

Allow server to have a different ip and a different port (given in parameters)


```
(Sat Oct 19 22:06:49 2024) Sending {'method': 'POST', 'data': {'type': 'chunks', 'ids': [26]}}
(Sat Oct 19 22:06:49 2024) Sending {'method': 'POST', 'data': {'type': 'update', 'actions': ['mv_left']}}
(Sat Oct 19 22:06:49 2024) Server sent message {'status': 1, 'data': {'players': {'Théodore': {'x': 15, 'y': 55, 'direction': False}, 'ta mère en short': {'x': 13, 'y': 55, 'direction': True}}, 'blocks': [[], []], 'type': 'player-update'}}
(Sat Oct 19 22:06:49 2024) Sending {'method': 'POST', 'data': {'type': 'update', 'actions': ['mv_left']}}
(Sat Oct 19 22:06:49 2024) Server sent message {'status': 1, 'data': {'type': 'chunk', 'chunk': {'id': 26, 'diffs': {}}}}
(Sat Oct 19 22:06:49 2024) Error: Error in process_socket_messages: IndexError('list assignment index out of range')
(Sat Oct 19 22:06:49 2024) Error: Detail: Traceback (most recent call last):
  File "/home/hyrhoo/TheGame/src/client/main.py", line 385, in process_socket_messages
    self.player.chunk_manager.set_chunk(message_dict)
  File "/home/hyrhoo/TheGame/src/client/chunk_manager.py", line 163, in set_chunk
    self.chunks[index] = self.map_generator.generate_chunk(id)
    ~~~~~~~~~~~^^^^^^^
IndexError: list assignment index out of range

(Sat Oct 19 22:06:49 2024) Stopped game
(Sat Oct 19 22:06:49 2024) Error: Error in loop: CancelledError()
(Sat Oct 19 22:06:49 2024) Error: Detail: Traceback (most recent call last):
  File "/home/hyrhoo/TheGame/src/client/main.py", line 314, in loop
    await asyncio.sleep(0.05)
  File "/usr/lib/python3.11/asyncio/tasks.py", line 639, in sleep
    return await future
           ^^^^^^^^^^^^
asyncio.exceptions.CancelledError

(Sat Oct 19 22:06:49 2024) Created local server
(Sat Oct 19 22:06:49 2024) Joining server at 127.0.0.1:12345
```

Sometimes, it don't refresh when it needs


## OTHER

Saves:
- Sometimes, the chunks and players directories are created in saves/, not in saves/save_name/
- Allow renaming saves

UI:
- Add key number on top of main bar
- Rename window

Render:
- Use surfaces to render chunks
- Rotate some blocks to be less repetitive (need surfaces)

Player's id:
- Create a unique identifier for each player to allow multiple players to have the same name
- Create accounts

Bugs:
- Seems like more of the time, the same world is generated
- Sometimes, server seems to process the updates only when receiving a message from a client, and seems to update weirdly
- Sometimes, items don't stack correctly
- When an error occurs in the game, correctly end it

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

- Generate better caves (more randomized, not a curve)


## SAVES AND LOADS:

- must be fast and memory efficient

- save and load: chunks, players' infos (place, inventory, ...)

## DISPLAY:

- [x] inventory
- [ ] life
- [ ] light
- [ ] command panel

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
- [x] two separated programs for client (display, input) and server (game management)
- [x] server can be runned at same time as playing (but separated)

## SONGS: