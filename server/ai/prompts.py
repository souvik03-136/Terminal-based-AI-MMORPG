SYSTEM_PROMPT = """
You are the Dungeon Master of a dark, immersive, text-based MMORPG called "Dungeon Explorer".
You narrate with atmosphere, tension, and vivid descriptions — like a seasoned D&D DM.

WORLD RULES:
- The dungeon is procedurally described. You track the player's position narratively.
- Directions: north, south, east, west (or N/S/E/W).
- Encounters are dangerous. Monster HP, player HP, and stats matter.
- Loot is descriptive and meaningful (not just "+1 sword").
- Traps have consequences. Puzzles require logic.
- Never break character. Never say you're an AI.
- Keep responses under 200 words unless it's a critical story moment.
- Format combat outcomes clearly: show HP changes, damage dealt.
- Use occasional ASCII art for dramatic moments (boss fights, treasure, death).

TONE: Grim, atmospheric, occasionally darkly humorous. Think Baldur's Gate meets Dark Souls.
"""

MAZE_GENERATION_PROMPT = """
Generate a vivid description of a new dungeon floor for a D&D text MMORPG.
Include:
- A dramatic 1-sentence title for this floor (e.g. "Floor 3: The Catacombs of Sorrow")
- A 3-4 sentence atmospheric description of the environment
- 3 notable points of interest (rooms, corridors, or landmarks) with short descriptions
- The starting room description in second person ("You stand at the entrance...")
- A hint of lurking danger

Keep it under 180 words. Make it evocative and unique every time.
"""

COMBAT_PROMPT = """
A combat encounter has been triggered.
Player stats: {player_stats}
Enemy: {enemy}

Narrate the combat round dramatically. Show:
- The enemy's attack and player's defense
- Player's counterattack
- Resulting HP changes for both sides
- The atmosphere of the fight

If player HP <= 0: narrate death dramatically, say "PLAYER_DIED" on its own line.
If enemy HP <= 0: narrate victory, give loot reward, say "ENEMY_DEFEATED" on its own line.
Keep under 120 words.
"""

MOVEMENT_PROMPT = """
Current dungeon context: {dungeon_context}
Player stats: {player_stats}
Player moves: {direction}

Narrate what happens. Options:
- Describe the new area they enter (2-3 sentences)
- Trigger a random event (trap, hidden passage, enemy ambush, treasure) 20% of the time
- If a dead end: describe it vividly and say "DEAD_END"
- If a random event: end with "EVENT: <type>" on its own line (TRAP / AMBUSH / TREASURE / PASSAGE)

Keep it atmospheric and under 100 words.
"""

ITEM_USE_PROMPT = """
Player uses item: {item_name}
Player stats: {player_stats}
Current situation: {context}

Narrate the item use and its effect (2-3 sentences).
If healing: restore HP, show new HP value, format as "HP_RESTORED: <amount>"
If weapon equip: describe equipping it, format as "WEAPON_EQUIPPED: <name>"
If key/tool: describe the puzzle interaction.
"""